# Похожие объявления

```mermaid
sequenceDiagram
    participant B as Browser
    participant N as Nginx
    participant AD as Adser
    participant AN as Analizator

    B->>+N: Получить похожие объявления
    N->>+AD: Получить похожие объявления
    AD->>+AN: Найти похожие по индексу
    AN-->>-AD: Список id похожих объявлений
    AD-->>-N: 200 OK [похожие объявления]
    N-->>-B: 200 OK [похожие объявления]
```
