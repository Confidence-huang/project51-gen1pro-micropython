#include "ecovision_algorithm.h"
#include <string.h>

#define HALF_RANGE 0x80000000u
static const uint32_t stale_ms[EV_CHANNELS]={10000u,10000u,2000u,5000u};
static const int32_t lower[EV_CHANNELS]={-4000,0,0,0};
static const int32_t upper[EV_CHANNELS]={8500,10000,65535,20};
/* Diagnostic thresholds, not physically proven slew limits; never reject a
 * within-range step solely for exceeding them. */
static const int32_t jump[EV_CHANNELS]={200,1000,10000,20};
static int32_t median3(int32_t a,int32_t b,int32_t c) {
    int32_t t;
    if(a>b){t=a;a=b;b=t;} if(b>c){t=b;b=c;c=t;}
    if(a>b){t=a;a=b;b=t;} return b;
}
static void expire(EvChannel *c,unsigned id,uint32_t now) {
    if(!c->has_value){c->age_ms=UINT32_MAX;return;}
    c->age_ms=now-c->at_ms;
    if(c->age_ms>=stale_ms[id]) {
        c->valid=0; c->stable=0; c->used=0; c->next=0; c->reason|=EV_STALE;
    }
}
/* Returns 1 valid NEW sample, -1 new invalid sample, 0 absent/duplicate/old. */
static int update(EvChannel *c,const EvSample *x,unsigned id,uint32_t now) {
    uint32_t delta;
    int32_t diff;
    expire(c,id,now);
    if(!x->present)return 0;
    c->last_attempt=*x;
    if(now-x->at_ms>=HALF_RANGE) {c->reason|=EV_TIME;return 0;}
    if(c->has_seen) {
        delta=x->at_ms-c->seen_ms;
        if(!delta){c->reason|=EV_DUPLICATE;return 0;}
        if(delta>=HALF_RANGE){c->reason|=EV_TIME;return 0;}
    }
    c->has_seen=1; c->seen_ms=x->at_ms;
    c->reason=0; c->driver_reason=x->driver_reason;
    if(!x->valid)c->reason|=EV_DRIVER;
    if(x->value<lower[id]||x->value>upper[id])c->reason|=EV_RANGE;
    if(now-x->at_ms>=stale_ms[id])c->reason|=EV_STALE;
    if(c->reason) {
        c->valid=0;c->stable=0;c->used=0;c->next=0;
        return -1; /* keep last valid raw/value timestamp and provenance */
    }
    if(c->valid) {
        diff=x->value-c->raw;
        if(diff>jump[id]||diff< -jump[id])c->reason|=EV_JUMP;
    }
    c->raw=x->value;c->at_ms=x->at_ms;c->age_ms=now-x->at_ms;
    c->source=x->source;c->simulated=x->simulated;
    c->has_value=1;c->valid=1;
    c->history[c->next]=x->value;c->next=(uint8_t)((c->next+1u)%3u);
    if(c->used<3)c->used++;
    c->stable=(uint8_t)(c->used==3);
    c->filtered=(id==EV_VISION||!c->stable)?x->value:
        median3(c->history[0],c->history[1],c->history[2]);
    return 1;
}
void ev_init(EvState *s) {
    unsigned i; memset(s,0,sizeof *s);
    s->comfort.cold_c100=2000;s->comfort.hot_c100=2800;
    s->comfort.dry_rh100=3000;s->comfort.wet_rh100=7000;
    for(i=0;i<EV_CHANNELS;i++) {
        s->channel[i].reason=EV_MISSING;s->channel[i].age_ms=UINT32_MAX;
    }
}
void ev_reset_vision(EvState *s) {
    EvChannel *v=&s->channel[EV_VISION];
    memset(v,0,sizeof *v);v->reason=EV_MISSING;v->age_ms=UINT32_MAX;
    s->occupancy=EV_UNKNOWN;s->positive=0;s->zero_active=0;s->dwell_active=0;
    /* Do not clear fault timer, manual state, other channels or outputs. */
}
void ev_step(EvState *s,const EvInput *in,EvOutput *o) {
    unsigned i; int fresh[EV_CHANNELS],target=-1;
    uint8_t lost_vision, lost_temp;
    EvChannel *v=&s->channel[EV_VISION],*t=&s->channel[EV_TEMP];
    /* Check gap BEFORE update, so a late fresh frame cannot bridge timeout. */
    lost_vision=(uint8_t)(!v->valid||!v->has_value||in->now_ms-v->at_ms>=5000u);
    lost_temp=(uint8_t)(!t->valid||!t->has_value||in->now_ms-t->at_ms>=10000u);
    if(lost_temp)s->dwell_active=0;
    memset(o,0,sizeof *o);
    for(i=0;i<EV_CHANNELS;i++) {
        fresh[i]=update(&s->channel[i],&in->sample[i],i,in->now_ms);
        if(!s->channel[i].valid || !s->channel[i].stable ||
           s->channel[i].reason) o->degraded_mask|=(uint8_t)(1u<<i);
        if(s->channel[i].has_value&&s->channel[i].simulated)
            o->simulated_mask|=(uint8_t)(1u<<i);
    }
    if(lost_vision||!v->valid) {
        s->occupancy=EV_UNKNOWN;s->positive=0;s->zero_active=0;
    }
    if(fresh[EV_VISION]>0) {
        if(v->raw>0) {
            s->zero_active=0;
            if(s->positive<3)s->positive++;
            if(s->positive>=3)s->occupancy=EV_OCCUPIED;
        } else {
            s->positive=0;
            if(!s->zero_active){s->zero_active=1;s->zero_since=v->at_ms;}
            if(v->at_ms-s->zero_since>=30000u)s->occupancy=EV_VACANT;
        }
    }
    o->occupancy=s->occupancy;o->vision_valid=v->valid;o->temp_valid=t->valid;
    o->reasons|=EV_REASON_LIGHT_UNCALIBRATED;
    if(s->occupancy==EV_UNKNOWN||!v->valid) {
        o->affected_mask|=3;o->reasons|=EV_REASON_OCCUPANCY_UNKNOWN;
    }
    if(!t->valid){o->affected_mask|=1;o->reasons|=EV_REASON_TEMP_UNKNOWN;}
    if(t->valid) o->thermal=(uint8_t)(t->filtered<s->comfort.cold_c100?EV_COLD:
        t->filtered>=s->comfort.hot_c100?EV_HOT:EV_SUITABLE);
    if(s->channel[EV_RH].valid) {
        int32_t rh=s->channel[EV_RH].filtered;
        o->humidity_need=(uint8_t)(rh<s->comfort.dry_rh100?EV_DRY:
            rh>s->comfort.wet_rh100?EV_WET:EV_RH_SUITABLE);
    }
    if(!v->valid||!t->valid) {
        if(!s->fault_active){s->fault_active=1;s->fault_since=in->now_ms;}
        o->reasons|=EV_REASON_FAULT;
    } else s->fault_active=0;
    o->fan=(uint8_t)(in->fan_actual!=0);o->led=(uint8_t)(in->led_actual!=0);
    if(in->mode!=s->previous_mode)s->dwell_active=0;
    s->previous_mode=in->mode;
    if(in->mode==EV_LOCAL_OFF) {
        o->fan=0;o->led=0;o->apply_mask=3;o->reasons|=EV_REASON_LOCAL;
        s->dwell_active=0;return;
    }
    if(in->mode!=EV_AUTO) {
        o->reasons|=EV_REASON_MANUAL;s->dwell_active=0;return;
    }
    o->apply_mask=3;
    if(s->fault_active&&in->now_ms-s->fault_since>=60000u) {
        o->fan=0;o->led=0;s->dwell_active=0;return;
    }
    if(s->occupancy==EV_VACANT&&v->valid) {
        o->fan=0;o->led=0;o->reasons|=EV_REASON_VACANT;s->dwell_active=0;return;
    }
    if(s->occupancy==EV_OCCUPIED&&v->valid) {
        o->led=1;o->reasons|=EV_REASON_OCCUPIED;
        if(t->valid)target=t->raw>=2800?1:t->raw<=2700?0:-1;
    }
    if(target<0||target==o->fan){s->dwell_active=0;return;}
    if(!s->dwell_active||s->dwell_target!=(uint8_t)target) {
        s->dwell_active=1;s->dwell_target=(uint8_t)target;s->dwell_since=in->now_ms;
    }
    if(in->now_ms-s->dwell_since>=5000u) {
        o->fan=(uint8_t)target;o->reasons|=EV_REASON_TEMP;s->dwell_active=0;
    }
}
int ev_debounce(EvDebounce *s,uint32_t now,uint8_t level,uint32_t delay_ms) {
    level=(uint8_t)(level!=0);
    if(!s->initialized||level!=s->candidate) {
        s->initialized=1;s->candidate=level;s->since=now;
    }
    if(now-s->since>=delay_ms){s->stable=level;s->known=1;}
    return s->known?s->stable:-1;
}
