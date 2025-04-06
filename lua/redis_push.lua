local redis = require "resty.redis"
local uri = ngx.var.request_uri
local range = ngx.req.get_headers()["Range"]

-- Only run if Range header is present
if not range then return end

-- Parse Range values
local from, to = string.match(range, "bytes=(%d+)-(%d+)")
if not from or not to then return end

local chunk_key = "video:" .. uri .. ":chunk:" .. from .. "-" .. to

-- Connect to Redis
local red = redis:new()
red:set_timeout(1000)

local ok, err = red:connect("192.168.1.8", 6379)
if not ok then
    ngx.log(ngx.ERR, "Redis connection failed: ", err)
    return
end

-- Redis ACL auth (username + password)
local res, err = red:auth("default", "user")
if not res then
    ngx.log(ngx.ERR, "Redis auth failed: ", err)
    return
end

-- Check if chunk is already in Redis
local exists = red:exists(chunk_key)
if exists == 1 then return end

-- Store the key for body filter
ngx.ctx.redis_key = chunk_key
