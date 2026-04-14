# Лента объявлений (поиск + фильтрация)

```mermaid
sequenceDiagram
    participant B as Browser
    participant N as Nginx
    participant AD as Adser

    B->>+N: Получить объявления
    N->>+AD: Получить объявления
    AD-->>-N: 200 OK [список объявлений]
    N-->>-B: 200 OK [список объявлений]
```
