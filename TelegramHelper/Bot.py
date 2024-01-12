from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import ForceReply, Update

from TelegramHelper.TelegramHelper.Client import Client
from TelegramHelper.TelegramHelper.DicMetodo import DicMetodo

class Bot:
    def __init__(self,token:str,name=None,replyAllowed=True):
        self.Token=token;
        self.Application=Application.builder().token(token).build();
        self.Name=name;
        self.SelectArg=Bot._SelectArg;
        self.Default=DicMetodo();
        self.Commands={};
        self.ReplyAllowed=replyAllowed;
        self.ReplyTractament=lambda cli:"";
        method=lambda update,context:self._Execute(update,context);
        self.Application.add_handler(MessageHandler(filters.Text(), method));
        self.Application.add_handler(MessageHandler(filters.CONTACT, method));

    async def _Execute(self,update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            cli=Client.FromBot(context, update);
            command=None;
            if self.ReplyAllowed and (cli.IsAReply or cli.IsAReplyFromBot):
                await self.ReplyTractament(cli);
            else:
                if self.ReplyAllowed and cli.IsAReply and len(cli.Args)==0:
                    command=cli.ReplyCommand;
                    args=cli.ReplyArgs;
                else:
                    if cli.IsACommand:
                        command=cli.Command;
                    args=cli.Args;

                if command is None or command not in self.Commands:
                    await self.Default.Execute(self.SelectArg(args),cli);
                else:
                    await self.Commands[command](cli,args);
        except Exception as e:
            print(e);
            

    def AddCommand(self,command:str,method):
        self.Commands[command.lower()]=method;

    def AddCommands(self,dicCommands):
        for command in dicCommands:
            self.AddCommand(command, dicCommands[command]);

    def AddCommandPlus(self,command:str,dicMetodo:DicMetodo):
        metodo=lambda cli,args:dicMetodo.Execute(self.SelectArg(args),cli);
        self.AddCommand(command, metodo);

    def AddCommandsPlus(self,dicCommands):
        for command in dicCommands:
            self.AddCommandPlus(command, dicCommands[command]);

    def Start(self):
        
        if self.Name is not None:
            print("Start Bot "+self.Name);
        
        self.Application.run_polling();
    
    def Stop(self):
        self.Application.stop();
        if self.Name is not None:
            print("Stop Bot "+self.Name);
    @staticmethod
    def _SelectArg(args):
        result=None;
        if args is not None:
            if len(args)>1:
                result=" ".join(args);
            elif len(args)==1:
                result=args[0];
        return result;
