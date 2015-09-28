#Xiaoyu API Document

## Some constant numbers

### User permission

```
Blocked      -> -1, 
Unvalidated  ->  0, 
InProgress   ->  1, 
Validated    ->  2, 
Admin        ->  3
```

### User online status

```
Offline      ->  0,
Online       ->  1, 
HideToFriends->  2, 
HideToStrangers->3, 
HideToAll    ->  4
```

### User's degree

```
Unknown      ->  0, 
Bachelor     ->  1, 
Master       ->  2, 
Phd          ->  3
```

### Visibility of tweets, replies and messages

```
All          ->  0, 
FriendsOnly  ->  1, 
Mutual       ->  2
```

## User management

### Registration 

Step 1: Get verification code

- POST: `/api/user/verify`
- Data:

    `phone` - Phone number

- Return value:
    
    A JSON data. If the operation is successful then `data.code` will be `0` and `data.msg` is `OK`. Otherwise `data.code` is something else and you can get error message in `data.msg` field.

Step 2: Register

- POST: `/api/register`

- Data:

    * `phone` - Phone number
    * `password` - **MD5 hash** of password
    * `vcode` - Verification code

- On success:

    * `data.uid` - User id

- On failure:

    * `data.message` - Error message

### Log in

- POST: `/api/login`

- Data:

    * `phone` - Phone number
    * `password` - **MD5 hash** of password

- On success:

    * `data.uid` - User id

- On failure:

    * `data.message` - Error message

### Current user information

- GET/POST: `/api/user`

- Returned value:
    
    User object of the current user. For data structure of User please refer to `model.py`.

### User meta

- GET: `/api/user/meta`

- Data:

    * `uid` - Optional. Specify the UID of the user you'd like to get. If not specified this API will return the data of current user.

- Returned value:

    User Meta object of the current user.

### User extension

- GET: `/api/user/ext`

- Data:

    * `uid` - Optional. Specify the UID of the user you'd like to get. If not specified this API will return the data of current user.

- Returned value:

    User Ext object of the current user.

### User-array related operations

This section shows some user-related APIs that will return an array of data. For these APIs you are supposed to specify these two paramaters via GET method in other to limit the offset and numbers of elements:

    * `offset` - Offset. Specify 0 to get data from the beginning.
    * `limit` - Limit. Specify 0 to get 10 elements.

#### Get online users

- GET: `/api/user/onlines`

- Returned data: An array of meta information of online users. For data structure of user meta, please refer to `model.py`.

#### Get hot users

- GET: `/api/user/hot`

- Returned ata: An array of meta information of users who have the most numbers of upvotes.

#### Get recent logon users

- GET: `/api/user/recent_login`

- Returned data: An array of meta information of users who has logged in recently sorted descendly.

## Tweets

### Post a tweet

- POST: `/api/tweet/add`

- Data:

    * `content` Content of the tweet. It can't be empty
    * `photos` An **array** of URL of photos. Length should be less than 3. This is a compulsory field, and please pass an empty value when there is no photo.
    * `visibility` An integer value that represents visibility of this tweet. Please refer to first chapter of the doc. Defaults to `All`.

- Return value: The Tweet object

### Reply to a tweet

- POST: `/api/tweet/reply`

- Data:
    
    * `content` Content of the reply. It can't be empty.
    * `target` The ID of the tweet to which it replies.
    * `visibility` Integer value that represents visibility of this reply.

- Return value: The Reply object.

## Common information

### Horoscopes

- GET/POST: `/api/common/horoscope`

- Return value:

    Returns an array of all horoscopes, each of which contains two keys:
    * `data.id` - A unique identifer 
    * `data.name` - The name of the horoscope

### User license

- GET/POST: `/api/common/license`

- Return value:
    
    * `data.content` - The content of the user license

### Provinces

- GET/POST: `/api/common/province`

- Return value:

    Returns an array of all provinces, each item has:
    * `data.id` - The unique identifer of the province
    * `data.name` - The name of the province

### Cities

- GET: `/api/common/city?province=`

- Data:
    
    * `province` - The ID of the province to search for.

- Return value:
    
    Returns an array of all cities belonging to the specified province, each item has:
    * `data.id` - The unique identifer of the city
    * `data.name` - The name of the city

### Schools

- GET/POST: `/api/common/school`

- Return value:

    Returns an array of all universities, each item has:
    * `data.id` - The unique identifer
    * `data.name` - The name of the university

