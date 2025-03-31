local frameCount = 0
local lastFrame = 0
local timeWait = 0
--local handle = io.popen("python Main.py", "r")
host, port = "127.0.0.1", 5000
client = assert(socket.connect(host, port))

callbacks:add("frame", function()
  frameCount = frameCount + 1
  local message = "frame " .. frameCount
  
  local response = "null"
  --while response ~= "1" and response ~= "-1"   do
    --client:send(message .. "\n")
    --response = client:receive(1024)
  --end
  --client:send(message .. "\n")
  --local response = client:receive(1024)

  --client:send(message .. "\n")
  local response = client:receive(1024)
  local button = response

  if frameCount > 30 then
    frameCount = 0
    emu:clearKey(C.GBA_KEY.LEFT)
    emu:clearKey(C.GBA_KEY.RIGHT)
    emu:clearKey(C.GBA_KEY.DOWN)
    emu:clearKey(C.GBA_KEY.UP)
    emu:clearKey(C.GBA_KEY.A)
    emu:clearKey(C.GBA_KEY.B)
    while button == null do
      response = client:receive(1024)
      button = response
    end
  end
  
  if button ~= null then
    frameCount = 0
    console:log("Button: " .. button)
    if button == "0" then
      emu:addKey(C.GBA_KEY.LEFT)
    elseif button == "1" then
      emu:addKey(C.GBA_KEY.RIGHT)
    elseif button == "2" then
      emu:addKey(C.GBA_KEY.DOWN)
    elseif button == "3" then
      emu:addKey(C.GBA_KEY.UP)
    elseif button == "4" then
      emu:addKey(C.GBA_KEY.A)
    elseif button == "5" then
      emu:addKey(C.GBA_KEY.B)
    end
  end

  emu:screenshot("screenshot.png")
end)
