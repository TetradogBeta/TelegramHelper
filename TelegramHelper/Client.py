import os
import uuid
from telegram import KeyboardButton,ReplyKeyboardMarkup,ReplyKeyboardRemove,Update
from telegram.ext import  ContextTypes
from telegram.ext._utils.types import  BT

class Client:
    def __init__(self,bot,chatId:int):
        self.Bot:BT=bot;
        self.ChatId=chatId;
        self.Context=None;
        self.Update=None;
        self.Args=None;
        self.Command=None;
        self.Reply=None;
        self.ReplyCommand=None;
        self.ReplyArgs=None;
        self.ReplyId=None;
        self.ReplyFrom=None;
        self.User=None;
        self.Id=None;
        self.IsForwardMessage=False;
        self.Contact=None;
        self.LangCode=None;

    @property
    def IsAReplyFromBot(self):
        resp=self.ReplyId is not None;
        if resp:
            resp=self.ReplyFrom.id==self.Bot.id;
        return resp;
    @property
    def IsAReply(self):
        return self.Reply is not None and self.ReplyId is not None and self.ReplyFrom is not None;
    @property
    def IsFromBot(self):
        return self.Context is not None and self.Update is not None;
    @property
    def IsACommand(self):
        return self.Args is not None and self.Command is not None;


    def AddButton(self,btnName:str):
        replayKeyBoard= ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(btnName); 
        
    def StartContactRequest(self,text:str,btnName:str='Send contact'):
        replyMarkup = ReplyKeyboardMarkup([[KeyboardButton(text=btnName, request_contact=True)]],
                                            resize_keyboard=True);
        return self.Bot.send_message(chat_id=self.ChatId,text=text,reply_markup=replyMarkup);

    def FinishContactRequest(self,text:str):
        return self.Bot.send_message(chat_id=self.ChatId,text=text,reply_markup=ReplyKeyboardRemove());

    def ReplyWithText(self,chatIdToReply:int,text:str):
        return self.Bot.send_message(chat_id=self.ChatId,reply_to_message_id=chatIdToReply,text=text);

    def SendMessage(self,text: str):
        return self.Bot.send_message(chat_id=self.ChatId,text=text);

    def SendHtml(self,html:str):
        return self.Bot.send_message(chat_id=self.ChatId,text=html,parse_mode='HTML');
    
    def SendText(self,text:str):
        return self.SendMessage(text);

    def SendPhoto(self,photo,desc=""):
        return self._Send(photo, desc, self.SendByteArrayPhoto, self.SendUrlPhoto, self.SendFilePhoto);

    def SendVideo(self,video,desc=""):
        return self._Send(video, desc, self.SendByteArrayVideo, self.SendUrlVideo, self.SendFileVideo);

    def SendUrlPhoto(self,urlPhoto:str,desc=""):
        return self.Bot.send_photo(chat_id=self.ChatId,photo=urlPhoto,caption=desc);

    def SendUrlVideo(self,urlVideo:str,desc=""):
        return self.Bot.send_video(chat_id=self.ChatId,video=urlVideo,caption=desc);

    def SendFilePhoto(self,photoLocalPath:str,desc=""):
        method=lambda id,photoStream,desc:self.Bot.send_photo(chat_id=id,photo=photoStream,caption=desc);
        return self._SendFile(photoLocalPath,method,desc);

    def SendFileVideo(self,videoLocalPath:str,desc=""):
        method=lambda id,videoStream,desc:self.Bot.send_video(chat_id=id,video=videoStream,caption=desc);
        return self._SendFile(videoLocalPath,method,desc);


    def SendByteArrayPhoto(self,photoBytes:bytearray,desc=""):
        return self._SendByteArray(photoBytes, self.SendFilePhoto,desc);

    def SendByteArrayVideo(self,videoBytes:bytearray,desc=""):
        return self._SendByteArray(videoBytes, self.SendFileVideo,desc);

    def _Send(self,data,desc,sendByteArry,sendUrl,sendFile):
        result=None;
        if isinstance(data, bytearray):
            result=sendByteArry(data,desc);
        elif isinstance(data, str):
            if data.startswith("http"):
                result=sendUrl(data,desc);
            else:
                result=sendFile(data,desc);
        else:
            raise Exception("only byteArray and str (http or filePath)");
        
        return result;

    def _SendFile(self,pathFile:str,method,desc):
        file=None;
        try:
            file=open(pathFile,'rb');
            id= method(self.ChatId,file,desc);
        finally:
            if file is not None:
                file.close(); 
        return id;

    def _SendByteArray(self,bytesFile:bytearray,method,desc):
        fileName=str(uuid.uuid4());
        result=None;
        try:
            with open(fileName, 'wb') as f:
                f.write(bytesFile);
            try:
                result=method(fileName,desc);
            finally:
                os.remove(fileName);
        except:#lo tengo que poner
            pass;
        return result;



        
    @staticmethod
    def FromChatId(bot,chatId:int):
        return Client(bot,chatId);
    
    @staticmethod
    def FromBot(context:ContextTypes.DEFAULT_TYPE,update:Update):
        client= Client(context.bot,update.effective_chat.id);
        client.Context=context;
        client.Update=update;
        client.User=update.effective_user;
        client.Id=client.User.id;
        client.LangCode=update.effective_user.language_code;
        
        if context.args is not None:
            client.Args=context.args;
        else:
            if   update.effective_message.contact is not None:
                client.Contact={
                    "firstName":str(update.effective_message.contact.first_name),
                    "lastName":str(update.effective_message.contact.last_name),
                    "phone":str(update.effective_message.contact.phone_number),
                    "id":str(update.effective_message.contact.user_id),
                };
            elif update.message is not None and " " not in update.message.text:
                client.Args=[update.message.text];
            else:
                client.Args=update.message.text.split(" ");
        if client.Args is not None and len(client.Args)>0 and client.Args[0].startswith("/"):
            client.Command=str(client.Args[0][1:]).lower();
            client.Args=client.Args[1:];
        try:#más adelante si se puede mirar de tener todo el arbol de replicas así no faltará ningun mensaje
            reply=update.message.reply_to_message;
            try:
                client.Reply=reply.caption;
            except:
                client.Reply=reply.text;

            client.ReplyId=reply.message_id;
            client.ReplyFrom=reply.from_user;
            if client.Reply.startswith("/"):
                replyArgs=client.Reply.split(" ");
                client.ReplyCommand=str(replyArgs[0][1:]).lower();
                client.ReplyArgs=replyArgs[1:];
        except:
            pass;
        return client;
