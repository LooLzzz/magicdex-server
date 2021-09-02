# Magicdex Server API #

**This project is a WIP**

## Info ##

This repo is a part of a larger project called Magicdex.  
Feel free to contact me for any question.

---

## API Overview ##

* [Authentication](#authentication)
    * `/auth/users`
        * `GET`: Login using a username and password combination.
        * `POST`, `PUT`: Register a new user.
    * `/auth/jwt`
        * `GET`: Login using an access token.
* [Collections](#collections)
    * `/collections`
        * `GET`: Retrieve all cards from active user's collection.
        * `POST`, `PUT`: Insert/update cards in active user's collection.
        * `DELETE`: Clear active user's collection.
    * `/collections/<:card_id>`
        * `GET`: Retrieve a specific card from active user's collection.
        * `POST`: Update a specific card in active user's collection.
        * `DELETE`: Delete a specific card from active user's collection.
* [Cards](#cards)
    * `/cards/phash`
        * `GET`: Retrieves an initial phash pickle file.

---

## Authentication Endpoint <a name="authentication"></a> ##

### Register ###

Register a new user.

```
POST /auth/users HTTP/1.1
PUT /auth/users HTTP/1.1

Response:
{
    "msg": "user created",
    "username": {:string},
    "access-token": {:string}
}
```

#### Parameters ####

| Name     | Location   | Type       | Description |
|----------|------------|------------|-------------|
| username | JSON Body | `string` | - |
| password | JSON Body | `string` | - |

### Login ###

Login using an existing username & password combination.

```
GET /auth/users HTTP/1.1

Response:
{
    "msg": "successfuly logged in",
    "username": {:string},
    "access-token": {:string}
}
```

#### Parameters ####

| Name     | Location   | Type       | Description |
|----------|------------|------------|-------------|
| username | JSON Body / URL Arguments | `string` | - |
| password | JSON Body / URL Arguments | `string` | - |

### Re-Login ###

Re-login using a saved JWT Token.

```
GET /auth/jwt HTTP/1.1

Response:
{
    "msg": "successfuly logged in",
    "username": {:string}
}
```

#### Parameters ####

| Name     | Location   | Type       | Description |
|----------|------------|------------|-------------|
| Authorization | Header | `Bearer Access-Token` | The JWT token to be used for authentication. The value should be in the form of `"Bearer {token:string}"` |

---

## Collections Endpoint <a name="collections"></a> ##

### Get All Cards ###

Retrieves a list of all cards in the *active* user's collection.

```
GET /collections HTTP/1.1

Response:
[
    {
        "_id": {:string},
        "scryfall_id": {:string},
        "amount": {:int},
        "tag": [
            {:string},
            ...
        ],
        "condition": {:stringEnum[NM, LP, MP, HP, DAMAGED]},
        "foil": {:bool},
        "signed": {:bool},
        "altered": {:bool},
        "misprint": {:bool}
    },
    {...},
]
```

#### Parameters ####

| Name     | Location   | Type       | Description |
|----------|------------|------------|-------------|
| Authorization | Header | `Bearer Access-Token` | The JWT token to be used for authentication. The value should be in the form of `"Bearer {token:string}"` |

### Clear Collection ###

Clears the *active* user's collection.

```
DELETE /collections HTTP/1.1

Response:
[
    {
        "_id": {:string},
        "action": "DELETED",
    },
    {...},
]
```

#### Parameters ####

| Name     | Location   | Type       | Description |
|----------|------------|------------|-------------|
| Authorization | Header | `Bearer Access-Token` | The JWT token to be used for authentication. The value should be in the form of `"Bearer {token:string}"` |

### Add or Update Collection ###

Adds or updates cards in the *active* user's collection.

```
POST /collections HTTP/1.1
PUT /collections HTTP/1.1

Response:
[
    {
        "_id": {:string},
        "action": {:stringEnum[CREATED, UPDATED, DELETED, NOP]},
    },
    {...},
]
```

#### Parameters ####

| Name     | Location   | Type       | Description |
|----------|------------|------------|-------------|
| Authorization | Header | `Bearer Access-Token` | The JWT token to be used for authentication. The value should be in the form of `"Bearer {token:string}"` |
| cards | JSON Body | `List[Card]` | List of cards to be updated or inserted into collection. When inserting a new card, `_id` field should be empty. |

### Update A Card ###

Updates a specific card in the *active* user's collection.

```
POST /cards/<card_id> HTTP/1.1

Response:
{
    "_id": {:string},
    /* including all affected fields and their new values */
}
```

#### Parameters ####

| Name     | Location   | Type       | Description |
|----------|------------|------------|-------------|
| Authorization | Header | `Bearer Access-Token` | The JWT token to be used for authentication. The value should be in the form of `"Bearer {token:string}"` |
| scryfall_id | JSON Body | `string` | Scryfall's id for the card |
| amount | JSON Body | `int` \| `string` | Amount of copies of the same card. Can be a number for a set value or a string in the form of `"+X"`/`"-X"` for addition/subtraction. *See note below*. |
| tag | JSON Body | `Array[string]` | List of tags for the card. |
| condition | JSON Body | `stringEnum[NM, LP, MP, HP, DAMAGED]` | Card condition, one of: `{Near-Mint, Lightly-Played, Moderately-Played, Heavily-Played, Damaged}` |
| foil | JSON Body | `bool` | Is card a foil? |
| signed | JSON Body | `bool` | Is card signed? |
| altered | JSON Body | `bool` | Is card altered? |
| misprint | JSON Body | `bool` | Is card a misprint? |

* **Note: if `card.amount` will be set to a values lower than or equal to 0, the card will be removed from the collection instead.**

### Get A Card ###

Retrieves a specific card in the *active* user's collection.

```
GET /cards/<:card_id> HTTP/1.1

Response:
{
    "_id": {:string},
    "scryfall_id": {:string},
    "amount": {:int},
    "tag": [
        {:string},
        ...
    ],
    "condition": {:stringEnum[NM, LP, MP, HP, DAMAGED]},
    "foil": {:bool},
    "signed": {:bool},
    "altered": {:bool},
    "misprint": {:bool}
}
```

#### Parameters ####

| Name     | Location   | Type       | Description |
|----------|------------|------------|-------------|
| Authorization | Header | `Bearer Access-Token` | The JWT token to be used for authentication. The value should be in the form of `"Bearer {token:string}"` |

## Cards Endpoint <a name="cards"></a> ##

### Request Initial Phash Pickle ####

Retrieves an initial phash pickle file.  
Mostly used for an easier starting point when `magicdex-desktop` is installed on a new machine.

```
GET /cards/phash HTTP/1.1

303 Redirect: "https://github.com/LooLzzz/magicdex-server/raw/phash/border_crop.pickle"
```
