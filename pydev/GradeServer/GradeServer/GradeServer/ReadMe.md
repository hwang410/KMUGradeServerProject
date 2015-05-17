###When you upload problem archive file, the problem folder should be
```
<problem name>
	L <problem name>.txt
	L <problem name>.pdf(optional)
	L <problem name>_SOLUTION | <problem name>_CHECKER
```
Following is each items' description.
#### `1. <problem name>.txt`
  It contains <problem>'s meta information.<br>
  e.g. for problem "Hello World"<br>
  Hello World.txt contains
  ```
  Name=Hello World, Difficulty=1, SolutionCheckType=Solution, LimitedTime=3000, LimittedMemory=128
 ```
  You can set the problem's difficulty with integer(<10).<br>
  If the problem judges user's code with static output.txt file, then SolutionCheckType should be Solution. <br>
  If solution can be dynamic, then Checker is possible.<br>
  Give LimittedTime(ms) and LimittedMemory(MB).

#### `2. <problem name>.pdf`
  It contains problem's descriptions. Problem's few input/output cases can be attached. This will show up on problem page, unless you don't contain this file.

#### `3. <problem name>_SOLUTION | <problem name>_CHECKER`
  It contains its standard file for judging. It can be Solution or Checker up to the meta data in <problem name>.txt file.<br>
  If it is Solution, it will contain
 ```
  -- for each case
  <problem name>_case1_input.txt, 
  <problem name>_case2_input.txt,
  ....
  <problem name>_case1_output.txt,
  <problem name>_case2_output.txt,
  ...
  -- for all cases
  <problme name>_cases_total_inputs.txt
  <problem name>_cases_total_outputs.txt
 ```
  The number of each input case is up to administrator.
  All cases file contains all each case file. 

   
