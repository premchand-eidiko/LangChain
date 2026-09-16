# Sequential Chains and RunnableSequence

A sequential chain runs steps in order. Each step receives the previous step's
output, so the output type and shape form a contract between steps.

`RunnableSequence` can be built with `.pipe()` or with the `|` operator. This
lesson uses simple Python functions to make each transformation visible.

## Run

```bash
python3 main.py
```

## Practice

Insert a step that removes punctuation or changes the output format. Notice that
the next step must accept the new value.
