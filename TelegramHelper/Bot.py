from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters

from TelegramHelper.Client import Client
from TelegramHelper.DicMetodo import DicMetodo

class Bot:
    def __init__(self,token:str,name=None,replyAllowed=True):
        self.Token=token;
        self.Updater=Updater(token=self.Token,use_context=True);
        self.Dispatcher=self.Updater.dispatcher;
        self.Name=name;
        self.SelectArg=Bot._SelectArg;
        self.Default=DicMetodo();
        self.Commands={};
        self.ReplyAllowed=replyAllowed;
        self.ReplyTractament=lambda cli:"";
        method=lambda update,context:self._Execute(context,update);
        self.Dispatcher.add_handler(MessageHandler(Filters.text, method));

    def _Execute(self,context,update):
        try:
            cli=Client.FromBot(context, update);
            command=None;
            if self.ReplyAllowed and cli.IsAReply:
                self.ReplyTractament(cli);
            if self.ReplyAllowed and cli.IsAReply and len(cli.Args)==0:
                command=cli.ReplyCommand;
                args=cli.ReplyArgs;
            else:
                if cli.IsACommand:
                    command=cli.Command;
                args=cli.Args;

            if command is None or command not in self.Commands:
                self.Default.Execute(self.SelectArg(args), cli);
            else:
                self.Commands[command](cli,args);
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

    def Start(self,wait=True):
        self.Updater.start_polling();
        if self.Name is not None:
            print("Start Bot "+self.Name);
        if wait:
            self.Updater.idle();
    
    def Stop(self):
        self.Updater.stop();
        if self.Name is not None:
            print("Stop Bot "+self.Name);
    @staticmethod
    def _SelectArg(args):
        result=None;
        if len(args)>1:
            result=" ".join(args);
        elif len(args)==1:
            result=args[0];
        return result;