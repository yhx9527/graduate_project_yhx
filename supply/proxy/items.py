from scrapy import Item, Field

class UserItem(Item):
    table='users'
    user_id = Field()
    nickname = Field()
    unique_id = Field()
    gender = Field()
    birthday = Field()
    signature = Field()
    school_name = Field()
    aweme_count = Field()
    total_favorited = Field()
    following_count = Field()
    aweme_fans = Field()
    news_article_fans = Field()
    live_stream_fans = Field()
    mplatform_followers_count = Field()
    country = Field()
    province = Field()
    city = Field()
    location = Field()
    district = Field()
    custom_verify = Field()
    with_fusion_shop_entry = Field()
    with_commerce_entry = Field()
    avatar = Field()
    share_url = Field()

class CommentItem(Item):
    table='comments'
    cid = Field()
    aweme_id = Field()
    user_id = Field()
    text = Field()
    create_time = Field()
    digg_count = Field()
    reply_id = Field()
    user_digged = Field()
    reply_comment_total = Field()

class PostItem(Item):
    table='posts'
    aweme_id = Field()
    user_id = Field()
    create_time = Field()
    desc = Field()
    music_author = Field()
    music_author_uid = Field()
    music_url = Field()
    duration = Field()
    comment_count = Field()
    digg_count = Field()
    download_count = Field()
    share_count = Field()
    forward_count = Field()
    text_extra = Field()
    dynamic_cover = Field()

class UrlTaskItem(Item):
    table='urltasks'
    url = Field()
    user_id = Field()
    crawl_count = Field()
    num = Field()
