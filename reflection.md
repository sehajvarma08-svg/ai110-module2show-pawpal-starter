# PawPal+ Project Reflection

## 1. System Design
Three Things the user should be able to do include:
Possible Ideas:  
    - add a pet
    - Genrate a daily plan/schedule for that pet 
    - book playdates with other dogs for that pet 
    - display that schedule 
    - schedule appoinments/ and or walks 
Three Core Things: 
    - Add a Pet 
    - Alter the Schedule of the said pet (walks, docotr appoinments, playdates, etc)
    - Display that Schedule
Other features I should consider adding: 
    - Conflict detection: warn if two tasks overlap, or if a playdate lands during a vet appointment.
    - Priority and status: so the plan can put a vet visit ahead of an optional playdate and show what's done.
    - Recurring tasks: daily feeding and walks shouldn't have to be re-entered each day.
    - Multiple pets: the Owner → Pet → Task relationship handles this without changes.
Main Objects for the system include: 
    - Attributes: the type of pet, pet name, pet breed, the color, mecial history; essentially everyhting about the pet 
    - Methods: Owner, Pet, Task/Event, Scheduler -- the four main classes  


**a. Initial design**

- Briefly describe your initial UML design.
    The Initial UML design i have 4 classes, including owner, the pet, the task, and the schdeuler. Each class has it own attributes including the owners infromation like name in the owner class, all of the pets information in the pet class, the tpe of task/time of the task in the tak class, and the ways to sort the class in the scheduler class. All of this make the back end of the pet care app. 
- What classes did you include, and what responsibilities did you assign to each?
    - So going off the previous question, I included a ttoal of four classes including the onwer, the pet, the tast and the scheduler. Essentially the onwer class has all the details of the owner; the paet class has all the details of the pet; the task class has all the details about the tast at hand that needs to be added; and the schduler has all the detials that help place the task in the schedule say based on priorty or time. 

**b. Design changes**

- Did your design change during implementation? Yes. i did. 
- If yes, describe at least one change and why you made it.
Tasks now know their pet

1. Task has a pet field, and Pet has an owner field, so you can go from a task back to its pet and owner.
Plans and explanations can now say "Walk Mochi" instead of just "Walk".
Proper choices instead of loose strings

2. Priority, recurrence and task type are now enums: Priority (LOW, MEDIUM, HIGH), Recurrence (NONE, DAILY, WEEKLY) and TaskType.
Priority now sorts correctly (high before low). Before, strings would have sorted alphabetically.
Unique task IDs

3. Every Task gets an id, so two identical tasks like two "Feed" entries can be told apart.
    remove_task is meant to match on id.
    Easier conflict checking

4. Task.end_time is a property (start plus duration).
        Task.overlaps(other) checks whether two tasks collide.
        detect_conflicts now returns pairs of clashing tasks, and its docstring says to sort by time and compare neighbors.

5. Recurring tasks
mark_complete() now returns the next occurrence for a recurring task, or None otherwise.
Plans that explain themselves

6. There's a new DailyPlan class holding the day, the scheduled tasks, the skipped tasks and the total minutes. A new SkippedTask class records each skipped task with a reason.
    build_daily_plan(day) returns a DailyPlan and saves it as Scheduler.last_plan. It takes a day, so "daily" is now defined.
    explain_plan() uses the saved plan, so it doesn't have to recompute.
    Smaller fixes

7. get_upcoming_tasks(now) takes now as a parameter, which makes it testable.
    The sort methods can take a list of tasks to sort.
    add_pet and add_task are meant to set the back-links and skip duplicates, and get_tasks() is meant to return a copy.





---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

The scheduler looks at three things: the owner's time left in the day, each task's priority, and whether two tasks overlap. It only plans tasks that are not done yet and are due on that day.

- How did you decide which constraints mattered most?

I put priority first because a high-priority task, like medication, should not be dropped just because it was added late. The time limit comes next because the owner only has so many minutes. Overlaps matter too, since one person can't do two tasks at once.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.


The scheduler adds tasks one by one, highest priority first, and skips a task if it doesn't fit or overlaps one already chosen. This is simple, but it is not always the best fit. A skipped task is not moved to another time, so a smaller set of tasks might have fit better.

- Why is that tradeoff reasonable for this scenario?
This is fine for a busy pet owner. The plan is easy to understand, and the app tells the owner why each task was skipped, so they can change the time themselves.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I used AI to mkae classes, make me pytest, make me the UML, and help me with the backend. It helped me debug and find any erros in the logic and maed the code overall cleaner. 
- What kinds of prompts or questions were most helpful?
The ones that made me double chack the code. For example, as i was finishing up the checkpoints one of the instructions were to question our AI(Claude) and see for any logical erros before moving forward. And that really hlepd, becuase had i not done that the app would have probabaly crashed going forward. 

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
Honeslty, there wasnt much i rejected. Although, i did ask claude to revise and redo some aspects beofre finally accpeting. Like for example, i initally had 4 classes and when i asked claude to make me a uml it made me one with 5 diffrent classes instead. So i ahd to let it know what it did and it than gave me the correct UML. Overall, i accpeted pretty much everything, as it was all quite effecinet. 
- How did you evaluate or verify what the AI suggested?
I mainly verfied what the AI was doing with the instructions that were given to us and through reading through the code and seeing if evrything seems right.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
I tested the core task and pet behaviors (completing tasks, adding tasks to pets), the recurring-task logic (daily and weekly repeats, no duplicate occurrences on repeated completion, correct next dates after late completion, and completing projected copies), and the scheduler's conflict handling (suggesting free slots when tasks overlap, and letting medication bypass the time budget). These were important because recurrence and conflict detection are where the scheduler is most likely to go wrong silently. A duplicated or mis-dated task, or a double-booked slot, would break the plan without raising any error.
- Why were these tests important?
These tests were important because the scheduler's riskiest failures are silent ones. A duplicated or mis-dated recurring task, a double-booked slot, or a medication dropped for time would all produce a plausible-looking schedule that is wrong, so nothing would signal the bug. Automated tests let me check those cases every time I changed the code, instead of relying on reading the output by eye. The basic completion and add-task tests gave me a reliable foundation for the more complex scheduling logic.
**b. Confidence**

- How confident are you that your scheduler works correctly? 4
- What edge cases would you test next if you had more time? If I had more time, I would test the boundaries and empty cases the current tests skip. These include back-to-back tasks that touch but don't overlap, a fully booked day with no free slot, tasks that cross midnight, and recurrence across month boundaries. I would also test conflicts across multiple pets, empty pets and schedules, and invalid input such as zero-length durations.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
