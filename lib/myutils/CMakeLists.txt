project(myutils)

set(SRC 
  mprpc.cpp
  mprpc.h
  shm_queue.h
  socket_connection.cpp
  socket_connection.h
  socketutils.cpp
  socketutils.h
  stringutils.h
  filemapping.cpp
  filemapping.h
  misc.cpp
  misc.h
  ipc_connection.cpp
  ipc_connection.h
  unicode.cpp
  unicode.h
  csvparser.cpp
  csvparser.h
  timeutils.h
  loop/AsyncCall.h
  loop/MessageLoop.cpp
  loop/MessageLoop.h
  loop/MsgLoopFuture.h
  loop/MsgRunLoop.h
  loop/RunLoop.cpp
  loop/RunLoop.h
  )

include_directories( . )

add_library(myutils STATIC ${SRC})

if (UNIX)
  if (NOT APPLE) 
    target_link_libraries(myutils rt)
  endif()
endif()
