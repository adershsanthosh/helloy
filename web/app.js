(() => {
  const wsUrl = 'ws://localhost:6789';
  const apiUrl = 'http://localhost:8000/api/messages';
  const uploadUrl = 'http://localhost:8000/api/upload';
  let name = null;
  let ws = null;
  const input = document.getElementById('input');
  const form = document.getElementById('form');
  const messages = document.getElementById('messages');
  const userNameEl = document.getElementById('userName');

  function appendSystem(text){
    const el = document.createElement('div');
    el.className = 'system';
    el.textContent = text;
    messages.appendChild(el);
    messages.scrollTop = messages.scrollHeight;
  }

  function appendMessage(msg, sender, timestamp = null){
    const wrapper = document.createElement('div');
    wrapper.className = 'bubble ' + (sender === name ? 'me' : 'other');

    const meta = document.createElement('div');
    meta.className = 'meta-row';
    const nm = document.createElement('div'); nm.className='name'; nm.textContent = sender;
    let timeStr = timestamp 
      ? new Date(timestamp).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})
      : new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});
    const time = document.createElement('div'); time.className='time'; time.textContent = timeStr;
    meta.appendChild(nm); meta.appendChild(time);

    const text = document.createElement('div'); text.textContent = msg;

    wrapper.appendChild(meta);
    wrapper.appendChild(text);
    messages.appendChild(wrapper);
    messages.scrollTop = messages.scrollHeight;
  }

  function appendFileMessage(filename, sender, filetype, url){
    const wrapper = document.createElement('div');
    wrapper.className = 'bubble ' + (sender === name ? 'me' : 'other');

    const meta = document.createElement('div');
    meta.className = 'meta-row';
    const nm = document.createElement('div'); nm.className='name'; nm.textContent = sender;
    const time = document.createElement('div'); time.className='time'; time.textContent = new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});
    meta.appendChild(nm); meta.appendChild(time);

    const fileDiv = document.createElement('div');
    fileDiv.className = 'file-message';
    
    if(filetype === 'image'){
      const img = document.createElement('img');
      img.src = url;
      img.style.maxWidth = '200px';
      img.style.borderRadius = '8px';
      img.onclick = () => window.open(url, '_blank');
      fileDiv.appendChild(img);
    }else if(filetype === 'video'){
      const video = document.createElement('video');
      video.src = url;
      video.controls = true;
      video.style.maxWidth = '200px';
      video.style.borderRadius = '8px';
      fileDiv.appendChild(video);
    }else{
      const link = document.createElement('a');
      link.href = url;
      link.textContent = '📎 ' + filename;
      link.target = '_blank';
      fileDiv.appendChild(link);
    }

    wrapper.appendChild(meta);
    wrapper.appendChild(fileDiv);
    messages.appendChild(wrapper);
    messages.scrollTop = messages.scrollHeight;
  }

  async function loadHistory(){
    try{
      const res = await fetch(apiUrl);
      const history = await res.json();
      history.forEach(m => appendMessage(m.text, m.sender, m.timestamp));
    }catch(e){
      console.log('No previous messages');
    }
  }

  async function uploadFile(file){
    const formData = new FormData();
    formData.append('file', file);
    formData.append('sender', name);

    appendSystem('Uploading ' + file.name + '...');
    
    try{
      const res = await fetch(uploadUrl, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      
      if(data.success){
        appendSystem('File uploaded: ' + file.name);
        // Send file info via WebSocket
        ws.send(JSON.stringify({
          type: 'file',
          filename: data.filename,
          filetype: data.filetype,
          url: data.url
        }));
      }
    }catch(e){
      appendSystem('Upload failed: ' + e.message);
    }
  }

  function connect(){
    ws = new WebSocket(wsUrl);
    ws.addEventListener('open', ()=>{
      ws.send(JSON.stringify({type:'join', name}));
      appendSystem('Connected to server');
      loadHistory();
    });

    ws.addEventListener('message', (ev)=>{
      try{
        const data = JSON.parse(ev.data);
        if(data.type === 'system') appendSystem(data.text);
        else if(data.type === 'msg') appendMessage(data.text, data.name);
        else if(data.type === 'file') appendFileMessage(data.filename, data.name, data.filetype, data.url);
      }catch(e){ console.error(e) }
    });

    ws.addEventListener('close', ()=>appendSystem('Disconnected'));

    form.addEventListener('submit', (e)=>{
      e.preventDefault();
      const val = input.value.trim();
      if(!val) return;
      ws.send(JSON.stringify({type:'msg', text:val}));
      input.value = '';
    });
  }

  function init(){
    name = localStorage.getItem('helloy_name') || prompt('Enter your display name') || 'Guest';
    localStorage.setItem('helloy_name', name);
    userNameEl.textContent = name;
    connect();
    
    // File upload handler
    const fileInput = document.getElementById('fileInput');
    fileInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if(file){
        uploadFile(file);
        fileInput.value = ''; // Reset for next file
      }
    });
  }

  init();
})();
