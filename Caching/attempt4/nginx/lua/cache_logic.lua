-- nginx/lua/cache_logic.lua
local redis = require "resty.redis"
local http = require "resty.http"

local args = ngx.req.get_uri_args()
local video = args["video"]
local chunk = args["chunk"]

if not video or not chunk then
    ngx.status = 400
    ngx.say("Missing parameters")
    return
end

local red = redis:new()
red:set_timeout(1000)
local ok, err = red:connect("redis", 6379)
if not ok then
    ngx.status = 500
    ngx.say("Redis connect failed: ", err)
    return
end

local key = "video:" .. video:gsub(" ", "_") .. ":chunk:" .. chunk
local chunk_data = red:get(key)

if chunk_data == ngx.null then
    -- Miss: trigger fetcher
    local httpc = http.new()
    local res, err = httpc:request_uri("http://192.168.1.8:5000/fetch", {
        method = "GET",
        query = {video = video, chunk = chunk}
    })

    ngx.status = 202
    ngx.say("Chunk is being fetched. Please retry shortly.")
    return
end

ngx.header["Content-Type"] = "video/mp4"
ngx.say(chunk_data)
