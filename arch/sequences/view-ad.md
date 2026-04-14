# Просмотр объявления

```mermaid
sequenceDiagram
    participant B as Browser
    participant N as Nginx
    participant AD as Adser
    participant P as Profiler

    B->>+N: Получить объявление
    N->>+AD: Получить объявление
    AD->>+P: Получить данные автора
    P-->>-AD: Данные автора
    AD-->>-N: 200 OK [объявление + данные автора]
    N-->>-B: 200 OK [объявление + данные автора]
```
