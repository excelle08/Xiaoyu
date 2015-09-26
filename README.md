#Xiaoyu API Document

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

