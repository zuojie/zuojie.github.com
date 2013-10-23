---
layout: default
title: Awesome Erlang Snippets
---
# {{ page.title }}
*{{ page.date | date_to_string }}*   
*Quick Sort*
```erlang
qsort([]) -> [];
qsort([H|T]) ->
	qsort4([X || X <- T, X =< H]) ++ [H] ++ qsort4([X || X <- T, X > H]).
```
