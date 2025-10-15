# Context Labels - Primary Organization

Contexts define WHERE, HOW, WITH WHOM, or WHEN a task can be done.

## Critical Format Rules

- Labels must be passed as a LIST: `["next", "yard", "home"]`
- NEVER as a single string like "@next @yard @home"
- Always strip @ prefix before passing to API
- Contexts are COMBINABLE for nuanced organization

## Location Contexts

- **@home**: Tasks done at home (general)
- **@house**: Tasks done inside the house
- **@yard**: Outdoor/garden tasks
- **@errand**: General errands (going out)
- **@bunnings**: Specific errand at Bunnings hardware store
- **@parents**: Errands at parents' house (Wendy & Ian)

## Activity Contexts

- **@computer**: Digital work/tasks
- **@email**: Email-specific actions
- **@call**: Phone calls needed
- **@chore**: Household chores
- **@maintenance**: Home/car/equipment maintenance

## People Contexts

- **@bec**: Tasks involving Bec (wife)
- **@william**: Tasks involving William (oldest son)
- **@reece**: Tasks involving Reece (middle son)
- **@alex**: Tasks involving Alex (youngest son)
- **@parents**: Also functions as errand context

## Special Contexts

- **@next**: Next action for a task/project (critical for GTD)
- **@waiting**: Waiting on someone/something (delegated or blocked)
- **@weather**: Weather-dependent tasks (outdoor work that can't be done in rain)
- **@nokids**: Tasks that require kids to be away (high-energy/disruptive)

## Energy Contexts (REQUIRED for all chores)

- **@lowenergy**: Tasks that don't take much energy to complete
- **@medenergy**: Tasks that take medium energy (moderate physical/mental effort)
- **@highenergy**: Tasks that take significant energy (physical or mental)

## Duration Contexts (REQUIRED for all chores)

- **@short**: Tasks that don't take much time (under 15 mins)
- **@medium**: Tasks that take 15 mins to 1 hour
- **@long**: Tasks that take over an hour to complete

## Combination Examples

- "Sweep under dining table" → @home @chore @medenergy @short
- "Fertilise lawn" → @yard @chore @weather @medenergy @medium
- "Ask Bec about dinner plans" → @bec @call @lowenergy @short
- "Buy paint at Bunnings" → @bunnings @errand @lowenergy @medium
- "Deep clean entire house" → @house @chore @highenergy @long @nokids
