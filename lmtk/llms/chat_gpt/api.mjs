import { ChatGPTAPIBrowser } from 'chatgpt';

let encode = msg => {
  // return Buffer.from(JSON.stringify(msg), 'utf-8').toString('base64');
  return JSON.stringify(msg);
};

let decode = msg => {
  // return JSON.parse(Buffer.from(msg, 'base64').toString('utf-8'));
  return JSON.parse(msg);
};

let sendMessage = msg => {
  return console.log(encode(msg));
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
  try {
    let streamedData = ''
    let result = await api.sendMessage(msg.prompt, {
      conversationId: msg.conversation_id,
      parentMessageId: msg.parent_message_id,
      onProgress(result) {
        streamedData += result.response;
        sendMessage({
          data: result.response,
          conversation_id: result.conversationId,
          message_id: result.messageId,
        });
      },
    });
    if (streamedData !== result.response) {
      sendMessage({
        data: result.response,
        conversation_id: result.conversationId,
        message_id: result.messageId,
      });
    }
  }
  catch(e) {
    console.error(e.stack);
  }
  finally {
    sendMessage({ end: true });
  }
};

// let ask = async msg => {
//   let i = 0;
//   let intervalID = setInterval(() => {
//     if (i >= 5) {
//       sendMessage({ end: true });
//       clearInterval(intervalID);
//       return;
//     }

//     sendMessage({
//       data: `${i}`,
//       conversation_id: 'asdf',
//       message_id: 'fffff',
//     });

//     i += 1;
//   }, 250);
// };

let data = '';
process.stdin.on('data', async chunk => {
  data += chunk;
  if (data.includes('\n')) {
    let msg = decode(data);
    data = '';
    await ask(msg);
  }
});

// await ask({
//   prompt: 'hello!',
//   conversation_id: '',
//   parent_message_id: '',
// })
