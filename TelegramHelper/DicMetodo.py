import re

class DicMetodo:
    def __init__(self):
        self.DicEnds={};
        self.DicStarts={};
        self.DicContains={};
        self.Regex={};
        self.Default=DicMetodo._Default;
    
    def AddStarts(self,starts:str,method):
        self.DicStarts[starts]=method;
    def AddEnds(self,ends:str,method):
        self.DicEnds[ends]=method;
    def AddContains(self,contains:str,method):
        self.DicContains[contains]=method;
    
    def AddRegex(self,regex:str,method):
        self.Regex[regex]=[re.compile(regex),method];
    
    async def Execute(self,text,args):
        encontrado=False;
        Result=None;
        if text is not None:
            for reg in self.Regex:
                if self.Regex[reg][0].match(text):
                    result=self.Regex[reg][1](args);
                    encontrado=True;
                    break;
            if not encontrado:
                for starts in self.DicStarts:
                    if text.startswith(starts):
                        result=self.DicStarts[starts](args);
                        encontrado=True;
                        break;
            if not encontrado:
                for ends in self.DicEnds:
                    if text.endswith(ends):
                        result=self.DicEnds[ends](args);
                        encontrado=True;
                        break;
            if not encontrado:
                for contains in self.DicContains:
                    if contains in text:
                        result=self.DicContains[contains](args);
                        encontrado=True;
                        break;
        if not encontrado:
            result=self.Default(args);

        return await result;

    @staticmethod
    def _Default(cli):
        pass;