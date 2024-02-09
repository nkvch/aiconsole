# The AIConsole Project
#
# Copyright 2023 10Clouds
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from fastapi.responses import JSONResponse

from aiconsole.api.endpoints.chats.chat import router

_log = logging.getLogger(__name__)


@router.post("/")
async def genui():
    return JSONResponse(
        content={
            "code": """
function Component() {
  // Initial state set to the current time
  const [_currentTime, _setCurrentTime] = React.useState(new Date());
  // useEffect to update the current time every second
  React.useEffect(() => {
    // Timer to update current time
    
    const _timer = setInterval(() => {
      _setCurrentTime(new Date());
    }, 1000);

    // Cleanup on unmount
    return () => clearInterval(_timer);
  }, []);

  // Format time as a string HH:MM:SS
  const _formatTime = (_date) => {
    return _date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false // 24 hour clock
    });
  };

  // Render the current time
  return (
    <div className="bg-blue" style={{ fontFamily: 'Monospace', fontSize: '24px', textAlign: 'center' }}>
      {_formatTime(_currentTime)}
    </div>
  );
}
"""
        }
    )
    return
