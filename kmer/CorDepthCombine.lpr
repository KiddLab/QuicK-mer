program CorDepthCombine;

{$mode objfpc}{$H+}

uses
  {$IFDEF UNIX}{$IFDEF UseCThreads}
  cthreads,
  {$ENDIF}{$ENDIF}
  Classes, SysUtils, CustApp
  { you can add units after this };

type

  { TMyApplication }

  TMyApplication = class(TCustomApplication)
  protected
    procedure DoRun; override;
  public
    constructor Create(TheOwner: TComponent); override;
    destructor Destroy; override;
    procedure WriteHelp; virtual;
  end;

{ TMyApplication }

procedure TMyApplication.DoRun;
var
  ErrorMsg: String;
  //Program Var
  liblist: TextFile;
  lib_file: array of File of Single;
  Combined: File of Single;
  libname: String;
  Output, Buffer: array[1..65536] of Single;
  I: QWord;
  J: Word;
  Read_size, Read_buf, K: Cardinal;
begin
  // quick check parameters
  ErrorMsg:=CheckOptions('hl','help');
  if ErrorMsg<>'' then begin
    ShowException(Exception.Create(ErrorMsg));
    Terminate;
    Exit;
  end;

  // parse parameters
  if HasOption('h','help') then begin
    WriteHelp;
    Terminate;
    Exit;
  end;

  { add your program here }
  if HasOption('l') then
    AssignFile(liblist,GetOptionValue('l'))
  else begin
    WriteHelp;
    Terminate;
    Exit;
  end;

  WriteLN('Load list: '+GetOptionValue('l'));
  Reset(liblist);
  I:=0;
  SetLength(lib_file,0);
  while not EOF(liblist) do
  begin
    ReadLN(liblist, libname);
    if FileExists(libname) then
    begin
      J:=Length(lib_file)+1;
      WriteLN(InttoStr(Length(lib_file)));
      SetLength(lib_file, J);
      
      AssignFile(lib_file[J-1],libname);
      Reset(lib_file[J-1]);
      WriteLN(libname);
      if I = 0 then
        I:=FileSize(lib_file[0])
      else if FileSize(lib_file[J-1]) <> I then
      begin
        WriteLN('File size inconsistant: '+libname+' '+IntToStr(FileSize(lib_file[J-1])));
        WriteLN('Other size: '+IntToStr(I)+' Bytes');
        Exit;
      end;
    end;
  end;

  CloseFile(liblist);
  if Length(lib_file) =0 then
  begin
    WriteLN('No file exist, exiting');
    Terminate;
    Exit;
  end;

  AssignFile(Combined,ChangeFileExt(GetOptionValue('l'),'_merged.bin'));
  WriteLN('File created for output');
  Rewrite(Combined);
  I:=0;

  repeat
    BlockRead(lib_file[0],Output[1],Length(Output),Read_size);
    for J := 1 to Length(lib_file)-1 do
    begin
      BlockRead(lib_file[J],Buffer[1],Length(Buffer),Read_buf);
      for K := 1 to Read_size do
      begin
        Output[K]:=Output[K]+Buffer[K];
      end;
    end;
    BlockWrite(Combined,Output[1],Read_size);
    Inc(I,Read_size);
  until EOF(lib_file[1]);
  //File Close
  for J := 0 to Length(lib_file)-1 do
  begin
    CloseFile(lib_file[J]);
  end;
  CloseFile(Combined);
  // stop program loop
  Terminate;
end;

constructor TMyApplication.Create(TheOwner: TComponent);
begin
  inherited Create(TheOwner);
  StopOnException:=True;
end;

destructor TMyApplication.Destroy;
begin
  inherited Destroy;
end;

procedure TMyApplication.WriteHelp;
begin
  { add your help code here }
  writeln('Usage: ',ExeName,' -h');
  WriteLN('Option:  -l [library.txt]');
  WriteLN('library.txt should contain each .bin file of equal size separate by lines');
end;

var
  Application: TMyApplication;
begin
  Application:=TMyApplication.Create(nil);
  Application.Title:='Combine Corrected Depth';
  Application.Run;
  Application.Free;
end.

