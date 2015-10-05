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

- POST: `/api/user/login`

- Data:

    * `phone` - Phone number
    * `password` - **MD5 hash** of password
    * `remember` - Whether to remember login status. 0 for not remember.

- On success:

    * `data.uid` - User id

- On failure:

    * `data.message` - Error message

### Log out

- GET/POST: `/api/user/logout`

- Will redirect to the homepage after this action

### Edit my information

- POST: `/api/user/meta/edit`

- Data:

    * Keys are property names of UserMeta object. Please refer to `model.py`.
    * If you don't want to change a certain field, you may leave it empty.
    * To change avatar please user `/api/photo/upload` to upload the avatar, after which you will get the returned URL.

- Return value:
    
    * The UserMeta object

### Change password

- POST: `/api/user/password/edit`

- Data:
    
    * `original` Password
    * `new` Retype password
    * `vcode` Verification code. You are required to do phone verification before requesting this API.

- Will log out and redirect to homepage after success.

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


### Update user's school information

- POST: `/api/user/school/edit`

- Data:
    
    * `school` - School ID
    * `degree` - Degree ID
    * `photo` - URL of validation photo

- Returned value: UserSchool object

### Get user's school information

- GET/POST: `/api/user/school/get`

- Data:

    * `uid` - Optional. User ID. Defaults to the current logged in user.

- Returned value: UserSchool object

### User-array related operations

This section shows some user-related APIs that will return an array of data. For these APIs you may specify these two paramaters via GET method in other to limit the offset and numbers of elements:

    * `offset` - Offset. Specify 0 to get data from the beginning. Defaults to 0.
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

## Wall

### Go upon the wall

- POST: `/api/wall/go`

- Data: 

    * `photos` - The array of JSON object string which contain photos URL and description message. No more than 8 pictures.
    * `title` - The name/title of the wall.

- Returned data: The Wall object

### Edit my filter

- POST: `/api/wall/edit_filter`

- Data: Specify one or more of them to restrict your filter:
    
    * `school` School ID
    * `degree` Degree ID
    * `gender` Gender.
    * `age_min` Minimum age
    * `age_max` Maximum age
    * `height_min` Minimum height
    * `height_max` Maximum height
    * `hometown_province` Province ID of hometown
    * `hometown_city`  City ID of hometown
    * `work_province` Province ID of work place
    * `work_city` City ID of work place
    * `horoscope` Horoscope ID

- Returned data: the Wall object

### Edit my photo

- POST: `/api/wall/edit_photo`

- Data:

    * `photos` - The array of photos URL.

- Returned Data: the Wall object

### Upvote someone

- GET/POST: `/api/wall/upvote`

- Data:
    
    * `uid` The User ID

- Returned value - the Wall object

### Get guest wall

- GET/POST: `/api/wall/guestwall`

- Returned value: An array of users to be displayed on the guest wall.

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

### Get tweets of my friends (including mine)

- GET/POST: `api/tweet/getall`

- Data:

    * `offset` Offset / Start from. Optional, and defaults to 0.
    * `limit` The number of tweets to return. Optional, and defaults to 0.
    * `later_than` **Timestamp** of the earliest tweet to get. In other words, all returned tweets are created later than this time. Optional, and defaults to 0.

- Return value: An array of Tweet objects

### Get tweets of someone

- GET/POST: `/api/tweet/user`

- Data:

    * `uid` The UID of the user.
    * `offset` Offset / Start from. Optional, and defaults to 0.
    * `limit` The number of tweets to return. Optional, and defaults to 0.
    * `later_than` **Timestamp** of the earliest tweet to get. In other words, all returned tweets are created later than this time. Optional, and defaults to 0.

- Return value: An array of his/her Tweet objects

### Get replies of a tweet

- GET/POST: `/api/tweet/reply/get`

- Data:

    * `id` The ID of the tweet
    * `offset` Offset / Start from. Optional, and defaults to 0.
    * `limit` The number of tweets to return. Optional, and defaults to 0.
    * `later_than` **Timestamp** of the earliest tweet to get. In other words, all returned tweets are created later than this time. Optional, and defaults to 0.

- Return value: An array of Reply objects that points to the tweet.

### Delete a tweet

- GET/POST: `/api/tweet/delete`

- Data:

    * `id` The ID of the tweet

- Return value: `data.id` - ID.

- NOTE: You must be the owner of the tweet to delete. After deletion all related replies will be deleted.

### Delete a reply.

- GET/POST: `/api/tweet/reply/delete`

- Data:

    * `id` The ID of the reply

- Return value: `data.id` - ID

- NOTE: You must be the owner of the reply, or owner of the tweet that the reply belongs to, to delete.

## User relationships (Friends, blacklists)

### Add a friend

- GET/POST: `/api/user/friends/add`

- Data:
    
    * `target` Target user ID.
    * `group` The ID of the group to which you want to add the friend. If not specified then this value would be 0 (Means regular friends)

- Return value: The Friend object

### Get all my friends

- GET/POST: `/api/user/friends`

- Return value: An array of all my accepted friends.

### Agree a friend-adding request

- GET/POST: `/api/user/friends/agree`

- Data:

    * `req_id` The friend-adding request ID
    * `group` The ID of group to which you want add the friend if you agree. Defaults to 0.

- Return value: The Friend object.

### Delete a friend

- GET/POST: `/api/user/friends/delete`

- Data:
    
    * `uid` The UID of the friend you want to remove

- Return value: `data.id` - The UID.

### Get my friend groups

- GET/POST: `/api/user/friends/groups`

- Return value: The array of all friend groups

- NOTE: The **index** of each group is very important, which serves as an identifer of the group.

### Add a friend group

- GET/POST: `/api/user/friends/groups/add`

- Data:
        
    * `title` - The title/name of the friend group

- Return value: The array of all friend groups

### Rename a friend group

- GET/POST: `/api/user/friends/groups/modify`

- Data:
    
    * `title` - The new title
    * `id` - The ID of the group to be modified

- Return value: The array of all friend groups

### Delete a friend group

- GET/POST: `/api/user/friends/groups/delete`

- Data:

    * `id` The ID of the group to be deleted

- Return value: The array of all friend groups

- NOTE: 
    
    * `id` CANNOT be zero, which points to the default friend group.
    * After deletion all friends belonging to this group will be moved to the **zeroth** default group.

## Photos and album

### Upload a photo

- POST: `/api/photo/upload`

- Data:

    * `photo` The photo file. Accepts only JPEG, GIF, PNG and TIFF formats.
    * Optional paramaters regarding to cropping and resizing:
        * `crop_left`, `crop_up`, `crop_right`, `crop_down` - Defines a 4-tuple defining the left, upper, right, and lower pixel coordinate to be cropped.
        * `resize_x`, `resize_y` - Width and height of resized image.

- Return value: The URL of saved photo.

- NOTE: This is a low-level API that only do the saving operation. You may need this API to upload a user's avatar, but remember that this does not insert to your album.

### Upload to album

- POST: `/api/album/upload`

- Data:

    * `photo` The photo file. Accepts only JPEG, GIF, PNG and TIFF formats.
    * `desc` Description of the photo
    * Optional paramaters regarding to cropping and resizing:
        * `crop_left`, `crop_up`, `crop_right`, `crop_down` - Defines a 4-tuple defining the left, upper, right, and lower pixel coordinate to be cropped.
        * `resize_x`, `resize_y` - Width and height of resized image.

- Return value: The Photo object

### Get all photos

- POST: `/api/album/get`

- Data: 

    * `uid` The UID of the user. If not specified, defaults to the current logged in user.

- Return value: The array of Photo objects beloging to the user.

### Delete a photo

- POST: `/api/album/delete`

- Data: 

    * `id` The ID of the photo to be deleted.

- Return value: `data.id` ID

- NOTE: You must be the owner to delete.

## Messages

### Leave a message

- POST: `/api/message/add`

- Data:

    * `uid` The UID of the user you wanna leave message to
    * `content` The content of message
    * `visibility` Visibility of message

- Return value: the Message object

### Reply to a message

- POST: `/api/message/reply/add`

- Data:

    * `id` The ID of the message you want to reply to
    * `content` Content. of reply
    * `visibility` Visibility

- Return value: the MessageReply object

### Get messages

- GET/POST: `/api/message/get`

- Data:
    
    * `uid` Optional. Specify the UID of user. Defaults to the current logged in user
    * `offset` Offset / Start from. Optional, and defaults to 0.
    * `limit` The number of tweets to return. Optional, and defaults to 0.
    * `later_than` **Timestamp** of the earliest tweet to get. In other words, all returned tweets are created later than this time. Optional, and defaults to 0.

- Return value: an array of Message objects

### Get replies of a message

- GET/POST: `/api/message/reply/get`

- Data:
    
    * `id` The ID of the message
    * `offset` Offset / Start from. Optional, and defaults to 0.
    * `limit` The number of tweets to return. Optional, and defaults to 0.
    * `later_than` **Timestamp** of the earliest tweet to get. In other words, all returned tweets are created later than this time. Optional, and defaults to 0.

- Return value: an array of MessageReply objects

### Delete a message

- GET/POST: `/api/message/delete`

- Data:
    
    * `id` The ID of the message

- Return value: `data.id` the ID

### Delete a reply

- GET/POST: `/api/message/reply/delete`

- Data:

    * `id` The ID of the reply

- Return value: `data.id` the ID


## Chat

### Send message

- POST: `/api/chat/send`

- Data:
    
    * `to` The UID of the friend to whom you send message.
    * `content` The content of message.

- Return value: `data.id` the ID

### Receive message

- GET/POST: `/api/chat/recv`

- Data:
    
    * `from` The UID of the friend from whom you receive messages. If not specified this will return ALL messages that send to you.

- Return value: An array of messages(ChatMessage object) that haven't been received.

## Notifications

### Get notificaitons

- GET/POST: `/api/notificaitons`

- Data:
    
    * `later_than` Optional. Get notificaitons sent later than this time.

- Return value: An array of Notification objects

## Abuse report

### Send abuse report

- POST: `/api/abuse_report`

- Data:
    
    * `target` UID of the target user.
    * `content` Complaint content

- Return value: the AbuseReport object

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

## Admin operations

### Send a notification

- GET/POST: `/api/admin/notificaiton/send`

- Data:
    
    * `content` - Content of notificaiton

- Return value: the Notification object

### Pass a user school info validation

- GET/POST: `/api/admin/school/verify`

- Data:
    
    * `uid` User ID

- Return value: the UserSchool object

### Process abuse reports

- GET/POST: `/api/admin/abuse_report/get`

- Data:
    
    * `filter_read` Filter out read items

- Return value: an array of AbuseReport objects

### Mark an abuse report as read

- GET/POST: `/api/admin/abuse_report/read`

- Data:
    
    * `id` ID of the item

- Return value: the AbuseReport object

### Set user permission

### Statistics

### Find an account by nickname