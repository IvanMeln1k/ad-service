# Закрытие и переоткрытие объявления

## Закрытие

```mermaid
sequenceDiagram
    participant B as Browser
    participant N as Nginx
    participant AD as Adser

    B->>+N: Закрыть объявление
    N->>+AD: Закрыть объявление
    AD-->>-N: 200 OK
    N-->>-B: 200 OK
```

## Переоткрытие

```mermaid
sequenceDiagram
    participant B as Browser
    participant N as Nginx
    participant AD as Adser

    B->>+N: Переоткрыть объявление
    N->>+AD: Переоткрыть объявление
    AD-->>-N: 200 OK
    N-->>-B: 200 OK
```
