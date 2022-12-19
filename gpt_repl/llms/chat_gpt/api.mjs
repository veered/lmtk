import { ChatGPTAPIBrowser } from 'chatgpt';

let encode = msg => {
  return Buffer.from(JSON.stringify(msg), 'utf-8').toString('base64');
};

let decode = msg => {
  return JSON.parse(Buffer.from(msg, 'base64').toString('utf-8'));
};

let startSession = async () => {
  let api = new ChatGPTAPIBrowser({
    email: process.env.OPENAI_EMAIL,
    password: process.env.OPENAI_PASSWORD
  })

  await api.initSession()
  return api;
};

let api = await startSession();

let ask = async msg => {
  const result = await api.sendMessage(msg.prompt, {
    conversationId: msg.conversation_id,
    parentMessageId: msg.parent_message_id,
  });
  return {
    response: result.response,
    conversation_id: result.conversationId,
    message_id: result.messageId,
  };
  return result;
};

let data = '';
process.stdin.on('data', async chunk => {
  data += chunk;
  if (data.includes('\n')) {
    let msg = decode(data);
    data = '';
    console.log(encode(await ask(msg)));
  }
});
