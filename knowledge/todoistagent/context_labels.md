# Context Labels - Decision Guide

Use this guide to disambiguate between similar contexts. The constrained tools enforce valid options via enums.

## Location Disambiguation

**@house vs @home vs @yard:**
- **@house**: Inside the house specifically (vacuuming, cleaning windows)
- **@home**: General home context when inside/outside distinction doesn't matter
- **@yard**: Outdoor/garden work specifically (mowing, gardening)

**@errand vs @bunnings vs @parents:**
- **@errand**: General errands/shopping (groceries, etc.)
- **@bunnings**: Specific trips to Bunnings hardware store
- **@parents**: Errands at parents' house (Wendy & Ian)

## Activity Disambiguation

**@chore vs @maintenance:**
- **@chore**: Routine cleaning/organizing tasks
- **@maintenance**: Fixing/repairing things that are broken

**@call vs @email:**
- **@call**: Requires phone call
- **@email**: Can be done via email

## Energy & Duration

**Energy levels** (required for chores):
- **@lowenergy**: Minimal effort
- **@medenergy**: Moderate effort
- **@highenergy**: Significant physical/mental effort

**Duration** (required for chores):
- **@short**: Under 15 minutes
- **@medium**: 15 minutes to 1 hour
- **@long**: Over 1 hour

## Special Contexts

- **@next**: This is the immediate next action (GTD critical)
- **@weather**: Weather-dependent outdoor work
- **@nokids**: Kids must be away (disruptive high-energy tasks)
- **@waiting**: Blocked/delegated, waiting on someone

## Combination Examples

- "Sweep under dining table" → @home @chore @medenergy @short
- "Fertilise lawn" → @yard @chore @weather @medenergy @medium
- "Ask Bec about dinner plans" → @bec @call @lowenergy @short
- "Buy paint at Bunnings" → @bunnings @errand @lowenergy @medium
- "Deep clean entire house" → @house @chore @highenergy @long @nokids
