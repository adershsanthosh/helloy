(() => {
  const wsUrl = 'ws://localhost:6789';
  let name = null;
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

  function appendMessage(msg, sender){
    const wrapper = document.createElement('div');
    wrapper.className = 'bubble ' + (sender === name ? 'me' : 'other');

    const meta = document.createElement('div');
    meta.className = 'meta-row';
    const nm = document.createElement('div'); nm.className='name'; nm.textContent = sender;
    const time = document.createElement('div'); time.className='time'; time.textContent = new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});
    meta.appendChild(nm); meta.appendChild(time);

    const text = document.createElement('div'); text.textContent = msg;

    wrapper.appendChild(meta);
    wrapper.appendChild(text);
    messages.appendChild(wrapper);
    messages.scrollTop = messages.scrollHeight;
  }

  function connect(){
    const ws = new WebSocket(wsUrl);
    ws.addEventListener('open', ()=>{
      ws.send(JSON.stringify({type:'join', name}));
      appendSystem('Connected to server');
    });

    ws.addEventListener('message', (ev)=>{
      try{
        const data = JSON.parse(ev.data);
        if(data.type === 'system') appendSystem(data.text);
        else if(data.type === 'msg') appendMessage(data.text, data.name);
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
  }

  init();
})();
