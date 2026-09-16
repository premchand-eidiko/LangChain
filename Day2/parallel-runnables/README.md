# RunnableParallel

`RunnableParallel` sends the same input to multiple named runnables and returns a
dictionary of results. It is useful when several independent tasks can run at
the same time, such as a summary, example, and interview question.

## Run

```bash
python3 main.py
```

## Practice

Add another named runnable. Notice that every branch receives the original
input, not the result from another branch. Use `RunnableSequence` inside a branch
when that branch needs multiple steps.
