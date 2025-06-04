import logo from './logo.svg';
import './App.css';
import { v4 as uuidv4 } from 'uuid';

//import styles from "@chatscope/chat-ui-kit-styles/dist/default/styles.min.css";
import './themes/default/main.scss';
import 'socket.io-client'
import {
  MainContainer,
  ChatContainer,
  MessageList,
  Message,
  Avatar,
  MessageInput,
} from "@chatscope/chat-ui-kit-react";
import { motion } from "motion/react"
import { useEffect, useState } from 'react';
import {socket} from './socket';

function App() {
  const animations = [{
    rotate: [0, 360],
    transition: { duration: 2 }
  },{
    scale: [1, 1.2, 1],
    transition: { duration: 2 }
  },
  {
    rotate: [0, 30, 0, -30, 0],
    transition: { duration: 2 }
  },
  {
    translateY: [0, "-35px", 0],
    transition: {duration: 0.5}
  }]

  const images = {claude:"../claude.png", gpt: "../gpt.jpg", gemini: "../gemini.png", User: "../sus.svg"}
  const [messages, setMessages] = useState([])

  const [connected, setConnected] = useState(false)

  const [disabledText, setDisabledText] = useState(false)

  function onConnection(){
    console.log("CONNECTED!!!")
    setConnected(true)
  }

  function onMessageEvent(v){
    console.log(v)
    setMessages(m => [...m, {...v, direction:"incoming"}])
  }

  function onDisconnect(){
    console.log("DISCONNECTED")
    setConnected(false)
  }

  useEffect(()=>{
    if(!socket.hasListeners()){
      socket.on('connect', onConnection)
      socket.on('message', onMessageEvent);
      socket.on('disconnect', onDisconnect)
    }
  },[])

  const [anim1, setAnim1] = useState({});
  const [anim2, setAnim2] = useState({});
  const [anim3, setAnim3] = useState({}); 

  function selectAnim1(){
    const index = Math.floor((Math.random() -0.001) * animations.length);
    setAnim1(animations[index])
  }

  function selectAnim2(){
    const index = Math.floor((Math.random() -0.001) * animations.length);
    setAnim2(animations[index])
  }

  function selectAnim3(){
    const index = Math.floor((Math.random() -0.001) * animations.length);
    setAnim3(animations[index])
  }

  useEffect(()=>{
    setInterval(()=>{
        selectAnim1()
        //setTimeout(selectAnim1, 1000 * (Math.floor((Math.random() -0.001) * 8)+ 3));
    }, 1000 * (Math.floor((Math.random()) * 5) + 3));
    setInterval(()=>{
      selectAnim2()
      //setTimeout(selectAnim2, 1000 * (Math.floor((Math.random() -0.001) * 8)+ 3));
    }, 1000 *(Math.floor((Math.random()) * 5) + 3));
    setInterval(()=>{
      selectAnim3()
      //setTimeout(selectAnim3, 1000 * (Math.floor((Math.random() -0.001) * 8)+ 3));
    }, 1000 *(Math.floor((Math.random()) * 5) + 3));
    setInterval(()=>{
      socket.send("ping")
    },5000)
  },[])

  return (
    <>
    <motion.div style={{position: "absolute", top: "12%", left: "44%", height: "22%", width: "12%"}}>
     <Avatar style={{width: "100%", height: "100%"}}
    name="Judge"
    src="../gpt.jpg"
  /></motion.div>
   <motion.div  animate={  {
    translateY: [0, "-15px", 0],
    transition: {duration: 0.5,repeatType: "loop", repeat: Infinity, delay: "5", repeatDelay: "8" }
  }} style={{position: "absolute", top: "-2%", left: "37%", height: "50%", width: "26%"}}>
     <Avatar style={{width: "100%", height: "100%"}}
    name="Wig"
    src="../wig.png"
  /></motion.div>
    <motion.div animate={anim1} style={{position: "absolute", top: "35%", left: "32%", height: "11%", width: "6%"}}>
     <Avatar style={{width: "100%", height: "100%"}}
    name="Gemini"
    src="../gemini.png"
  /></motion.div><motion.div animate={anim2} style={{position: "absolute", top: "35%", right: "32%", height: "11%", width: "6%"}}>
  <Avatar style={{width: "100%", height: "100%"}}
  name="GPT"
  src="../gpt.jpg"
/></motion.div>
<motion.div animate={anim3} style={{position: "absolute", bottom: "35%", left: "29%", height: "13%", width: "7%"}}>
<Avatar style={{width: "100%", height: "100%"}}
    name="Bot"
    src="../claude.png"
  />
  </motion.div>
    <div style={{display: "flex", justifyContent: "center", alignItems: "center", height: "100vh", width:"100vw"}}>
      <div className='App'  style={{display: "flex", justifyContent: "center", alignItems: "center", width: "50%", 
      height: "95%"}}>
      <div className='rotate' style={{ height: "430px", width: "385px", 
      marginBottom: "8vh"}}>
        
    <ChatContainer style={{height: "399px"}}>
      <MessageList>
        {
        messages.map((m)=> m.weaknesses && m.weaknesses.length > 0?
        <Message
          model={m} key={uuidv4()}
        >
              <Message.CustomContent>
              <strong>{m.sender}</strong><br/>
              <strong style={{color: "red"}}>Weaknesses:</strong>
              <ul>
              {Object.entries(m.weaknesses).map((e)=>{
                return(<li key={uuidv4()}>
                  <strong>{e[0]}</strong>: {e[1]}
                </li>)
              }
              )}
              </ul>
              <strong style={{color: "green"}}>Strengths:</strong>
              <ul>
              {Object.entries(m.strengths).map((e)=>{
                return(<li key={uuidv4()}>
                  <strong>{e[0]}</strong> : {e[1]}
                </li>)
              }
              )}
              </ul>
            </Message.CustomContent>
            <Avatar
    name="Bot"
    src={images[m.name]}
  />
        </Message> : <Message
          model={m}
        >
              <Message.CustomContent>
              <strong>{m.name}</strong><br/>
              {m["old answer"]? m["old answer"] : m.message? m.message.replace("<br>", " ") : m.message}
            </Message.CustomContent>
            <Avatar
    name="Bot"
    src={images[m.name]}
  />
        </Message>
        )}
      </MessageList>
      <MessageInput attachButton="false" disabled={disabledText} onSend={(v) => {
        setMessages([...messages, {
        message: v,
        sentTime: "just now",
        name: "User",
        direction: "outgoing"
      }]);
        setDisabledText(true)
        socket.send(v)
      }} placeholder="Type message here" >
      </MessageInput>
    </ChatContainer>
    </div>
    </div>
    </div>
    </>
  );
}

export default App;
