# Magicdex Server API #

![version](https://img.shields.io/badge/version-pre--alpha-blue)  
![build](https://img.shields.io/badge/build-passing-green)

**This project is a WIP**

## Info ##

This repo is a part of a larger project called Magicdex.  
Feel free to contact me for any question.

---

## API Overview ##

* [Authentication](#authentication)
    * `/auth/users`
        * `GET`: Login using a username and password combination.
        * `PUT`: Register a new user.
    * `/auth/jwt`
        * `GET`: Login using an access token.
* [Collections](#collections)
    * `/collections`
        * `GET`: Retrieve cards from active user's collection.
        * `PUT`, `POST`: Insert/update cards in active user's collection.
        * `DELETE`: Delete cards from active user's collection.
    * `/collections/all`
        * `GET`: Retrieve **all** cards from active user's collection.
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
PUT /auth/users HTTP/1.1

Response:
{
    "msg": "user created",
    "username": {:string},
    "access-token": f'Bearer {:string}'
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
    "access-token": f'Bearer {:string}'
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

### Get Cards ###

Retrieves a list of cards in the *active* user's collection.  
Supports pagination.

```
GET /collections HTTP/1.1

Response:
{
    "page": {:int},
    "per_page": {:int},
    "total_documents": {:int}, /* only present in the first page */
    "next_page": {:stringUrl}, /* not present in the last page */
    "data": [
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
}
```

#### Parameters ####

| Name     | Location   | Type       | Default Value | Description |
|----------|------------|------------|---------------|-------------|
| Authorization | Header | `Bearer Access-Token` | - | The JWT token to be used for authentication. The value should be in the form of `"Bearer {token:string}"` |
| page      | JSON Body / URL Arguments | `int`  | `1`  | Pagination page number, indexing starts from 1 |
| per_page  | JSON Body / URL Arguments | `int`  | `20` | Amount of cards per page |

### Get All Cards ###

Retrieves all cards in the *active* user's collection.  
Does not use pagination.

```
GET /collections/all HTTP/1.1

Response:
{
    "total_documents": {:int},
    "data": [
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
}
```

#### Parameters ####

| Name     | Location   | Type       | Description |
|----------|------------|------------|-------------|
| Authorization | Header | `Bearer Access-Token` | The JWT token to be used for authentication. The value should be in the form of `"Bearer {token:string}"` |

### Clear Collection ###

Clears the *active* user's collection.

```
DELETE /collections/all HTTP/1.1

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

### Delete Cards ###

Deletes cards from *active* user's collection.

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
| cards | JSON Body | `List[Card]` | List of cards to be deleted from the collection. Only `Card.card_id` is actually used for the deletion operation. |

### Add or Update Collection ###

Adds or updates cards in the *active* user's collection.

```
POST /collections HTTP/1.1
PUT  /collections HTTP/1.1

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
| cards | JSON Body | `List[Card]` | List of cards to be updated or inserted into collection. *See notes below*. |

**Notes:**

* Should be a list of cards, each object can contain any number of fields from `Update A Card` section.
* When inserting a new card:
    * `_id` field should be empty.
    * If a field is not present or `null`, it's default value will be used instead.

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

| Name     | Location   | Type       | Default Value | Description |
|----------|------------|------------|-------------|-------------|
| Authorization | Header | `Bearer Access-Token` | - | The JWT token to be used for authentication. The value should be in the form of `"Bearer {token:string}"` |
| scryfall_id | JSON Body | `string` | - | Scryfall's id for the card |
| amount | JSON Body | `int` \| `string` | `"+1"` | Amount of copies of the same card. Can be a number for a set value or a string in the form of `"+X"`/`"-X"` for addition/subtraction. *See note below*. |
| tag | JSON Body | `Array[string]` | `[]` | List of tags for the card. |
| condition | JSON Body | `stringEnum[NM, LP, MP, HP, DAMAGED]` | `"NM"` | Card condition, one of: `{Near-Mint, Lightly-Played, Moderately-Played, Heavily-Played, Damaged}` |
| foil | JSON Body | `bool` | `false` | Is card a foil? |
| signed | JSON Body | `bool` | `false` | Is card signed? |
| altered | JSON Body | `bool` | `false` | Is card altered? |
| misprint | JSON Body | `bool` | `false` | Is card a misprint? |

* **Note: if `card.amount` will be set to a value lower than or equal to 0, the card will be removed from the collection instead.**

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

308 Redirect: "https://github.com/LooLzzz/magicdex-server/raw/phash/border_crop.pickle"
```
