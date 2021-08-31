import os
import uuid


class Client:
    def __init__(self,bot,chatId:int):
        self.Bot=bot;
        self.ChatId=chatId;
        self.Context=None;
        self.Update=None;
        self.Args=None;
        self.Command=None;
    
    @property
    def IsFromBot(self):
        return self.Context is not None and self.Update is not None;
    @property
    def IsACommand(self):
        return self.Args is not None and self.Command is not None;
    def SendMessage(self,text: str)->int:
        return self.Bot.send_message(chat_id=self.ChatId,text=text);

    def SendPhoto(self,photo,desc="")->int:
        result=None;
        if isinstance(photo, bytearray):
            result=self.SendByteArrayPhoto(photo,desc);
        elif isinstance(photo, str):
            if "http" in photo:
                result=self.SendUrlPhoto(photo,desc);
            else:
                result=self.SendFilePhoto(photo,desc);
        else:
            yield Exception("only byteArray and str (http or filePath)");
        
        return result;

    def SendUrlPhoto(self,urlPhoto:str,desc=""):
        return self.Bot.send_photo(chat_id=self.ChatId,photo=urlPhoto,caption=desc);
    def SendFilePhoto(self,photoLocalPath:str,desc=""):
        photo=None;
        try:
            photo=open(photoLocalPath,'rb');
            id= self.Bot.send_photo(chat_id=self.ChatId,photo=photo,caption=desc);
        finally:
            if photo is not None:
                photo.close(); 
        return id;
    def SendByteArrayPhoto(self,photoBytes:bytearray,desc=""):
        fileName=str(uuid.uuid4());
        result=None;
        try:
            with open(fileName, 'wb') as f:
                f.write(photoBytes);
            try:
                result=self.SendFilePhoto(fileName,desc);
            finally:
                os.remove(fileName);
        except:#lo tengo que poner
            pass;
        return result;



        
    @staticmethod
    def FromChatId(bot,chatId:int):
        return Client(bot,chatId);
    
    @staticmethod
    def FromBot(context,update):
        client= Client(context.bot,update.effective_chat.id);
        client.Context=context;
        client.Update=update;
        if context.args is not None:
            client.Args=context.args;
        else:
            if " " not in update.message.text:
                client.Args=[update.message.text];
            else:
                client.Args=update.message.text.split(" ");
        if client.Args is not None and len(client.Args)>0 and client.Args[0].startswith("/"):
            client.Command=str(client.Args[0][1:]).lower();
            client.Args=client.Args[1:];
        return client;