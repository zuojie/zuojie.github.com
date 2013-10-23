---
layout: default
title: Awesome Erlang Snippets
---
# {{ page.title }}
*{{ page.date | date_to_string }}*   
###Quick Sort
```erlang
qsort([]) -> [];
qsort([H | T]) ->
	qsort([X || X <- T, X =< H]) ++ [H] ++ qsort([X || X <- T, X > H]).
```
