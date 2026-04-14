# Бан и разбан объявления

## Бан

```mermaid
sequenceDiagram
    participant M as Moderator
    participant N as Nginx
    participant AD as Adser
    participant A as Auther
    participant P as Profiler

    M->>+N: Забанить объявление
    N->>+AD: Забанить объявление
    AD->>+A: Валидировать токен
    alt Токен невалиден
        A-->>AD: 401 Unauthorized
        AD-->>N: 401 Unauthorized
        N-->>M: 401 Unauthorized
    else OK
        A-->>-AD: user_id
        AD->>+P: Получить роль
        alt Нет прав
            P-->>AD: 403 Forbidden
            AD-->>N: 403 Forbidden
            N-->>M: 403 Forbidden
        else OK
            P-->>-AD: role
            AD-->>-N: 200 OK
            N-->>-M: 200 OK
        end
    end
```

## Разбан

```mermaid
sequenceDiagram
    participant M as Moderator
    participant N as Nginx
    participant AD as Adser
    participant A as Auther
    participant P as Profiler

    M->>+N: Разбанить объявление
    N->>+AD: Разбанить объявление
    AD->>+A: Валидировать токен
    alt Токен невалиден
        A-->>AD: 401 Unauthorized
        AD-->>N: 401 Unauthorized
        N-->>M: 401 Unauthorized
    else OK
        A-->>-AD: user_id
        AD->>+P: Получить роль
        alt Нет прав
            P-->>AD: 403 Forbidden
            AD-->>N: 403 Forbidden
            N-->>M: 403 Forbidden
        else OK
            P-->>-AD: role
            AD-->>-N: 200 OK
            N-->>-M: 200 OK
        end
    end
```
