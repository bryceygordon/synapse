# Context Labels - Primary Organization

Contexts define WHERE, HOW, WITH WHOM, or WHEN a task can be done.

## Critical Format Rules

- Labels must be passed as a LIST: `["next", "yard", "home"]`
- NEVER as a single string like "@next @yard @home"
- Always strip @ prefix before passing to API
- Contexts are COMBINABLE for nuanced organization

## Location Contexts

- **@home**: Tasks done at home
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

- **@waiting**: Waiting on someone/something (delegated or blocked)
- **@weather**: Weather-dependent tasks

## Combination Examples

- "Sweep under dining table" → @home @chore
- "Fertilise lawn" → @yard @chore @weather
- "Ask Bec about dinner plans" → @bec @call
- "Buy paint at Bunnings" → @bunnings @errand
