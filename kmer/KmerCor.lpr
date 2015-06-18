program KmerCor;

{$mode objfpc}{$H+}

uses
  {$IFDEF UNIX}{$IFDEF UseCThreads}
  cthreads,
  {$ENDIF}{$ENDIF}
  Classes, SysUtils, CustApp{$IFDEF UNIX},
  { you can add units after this }
  Unix{$ENDIF};

type

  { TKmerPipeline }

  TKmerPipeline = class(TCustomApplication)
  protected
    procedure DoRun; override;
  public
    constructor Create(TheOwner: TComponent); override;
    destructor Destroy; override;
    procedure WriteHelp; virtual;
  end;

{ TKmerPipeline }

procedure TKmerPipeline.DoRun;
var
  ErrorMsg: String;
  //Variables
  CN2_flag: File of Byte;
  GC: array of Single;
  Excluded_flag: array [0..1048575] of Byte;
  GC_size, I: QWord;
  Read_size: Cardinal;
  jf_count: array of Word;
  Origin_time: TDateTime;
  //I: Longword;
  jf_input, GC_curve: Textfile;
  depth: Word;
  flag: Byte;
  line, jflib_name, kmer_seq, GC_filename, Exclude_filename: string;
  //for GC correction
  Cor_file, GC_file: File of Single;
  GC_bin: Word;
  Cor_dp: Single;
  binarr : array [0..400] of Extended;
  x2arr: array [0..400] of Extended;
  count : array [0..400] of Integer;
begin
  // quick check parameters
  ErrorMsg:=CheckOptions('hlkGE','help');
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

  //Check jf lib name
  if HasOption('l') and HasOption('k') and HasOption('G') and HasOption('E') then
  begin
    jflib_name:=GetOptionValue('l');
    WriteLN(#10+'File input: '+jflib_name);
    kmer_seq:=GetOptionValue('k');
    WriteLN('Kmer Seq: '+kmer_seq+#10);
    GC_filename:=GetOptionValue('G');
    Exclude_filename:=GetOptionValue('E');
  end
  else begin
    WriteHelp;
    Terminate;
    Exit;
  end;

  try
    Origin_time:=Now;
    AssignFile(GC_file,GC_filename);
    FileMode := fmOpenRead;
    Reset(GC_file);
    GC_size:=FileSize(GC_file);
    SetLength(GC,GC_size);
    I:=0;
    repeat
      if GC_size-I >= 131072 then
        BlockRead(GC_file,GC[I],131072,Read_size)
      else
        BlockRead(GC_file,GC[i],GC_size-I,Read_size);
      Inc(I,Read_size);
    until EOF(GC_file);
    CloseFile(GC_file);
    WriteLN('Kmer GC successfully loaded in '+TimeToStr(Now-Origin_time));

    SetLength(jf_count,GC_Size);
    WriteLN('Jellyfish count memory created');

    Origin_time:=Now;
    AssignFile(CN2_flag,Exclude_filename);
    FileMode := fmOpenRead;
    Reset(CN2_flag);
    if FileSize(CN2_flag) <> GC_size then
    begin
      WriteLN('CN2 flag file size error.');
      Terminate;
    end;
    //WriteLN('CN2 flag file loaded in '+TimeToStr(Now-Origin_time)+#10);

    //Iniatialize GC bins
    for I:=0 to 400 do
    begin
      binarr[I]:=0;
      count[I]:=0;
      x2arr[I]:=0;
    end;

    //Open jellyfish pipe in
    Origin_time:=Now;
    WriteLN('Start Jellyfish Pipe');
    {$IFDEF UNIX}POpen(jf_input,'cut -f5 '+kmer_seq+' | jellyfish-2 query -i '+jflib_name, 'R');
    {$ENDIF}
    WriteLN('cut -f5 '+kmer_seq+' | jellyfish-2 query -i '+jflib_name);
    I:=0;

    repeat
      if I mod 1048576 =0 then
        BlockRead(CN2_flag,Excluded_flag[0],1048576,Read_size);
      //Reading jellyfish input
      ReadLN(jf_input,line);
      depth:=StrToInt(line);
      jf_count[I]:=depth;

      //Check CN=2 region
      flag:=Excluded_flag[I mod 1048576];
      if flag = 0 then
      begin
        //increase GC bin
        GC_bin:=Round(GC[I]*4);
        binarr[GC_bin]:=binarr[GC_bin]+depth;
        x2arr[GC_bin]:=x2arr[GC_bin]+depth*depth;
        Inc(count[GC_bin]);
      end;

      Inc(I);
    until EOF(jf_input);
    {$IFDEF UNIX}PClose(jf_input); {$ENDIF}
    WriteLN('Jellyfish query completed in '+TimeToStr(Now-Origin_time));

    //Calculate GC curve
    Origin_time:=Now;
    AssignFile(GC_curve, ChangeFileExt(jflib_name, '.txt'));
    FileMode := fmOpenWrite;
    WriteLN('File open');
    Rewrite(GC_curve);
    for I := 0 to 400 do
    begin
      if count[I] >1 then
      begin
        x2arr[I]:=Sqrt((x2arr[I]-binarr[I]*binarr[I]/count[I])/(count[I]-1));
        binarr[I]:=binarr[I]/count[I];
      end
      else begin
        x2arr[I]:=0;
        binarr[I]:=0;
      end;
      WriteLn(GC_curve, FloatToStr(I/4)+#9+FloatToStr(binarr[I])+#9+IntToStr(count[I])+#9+FloatToStr(x2arr[I]));
    end;
    Close(GC_curve);
    WriteLN('GC curve completed');

    //Call external Python script for correction factor
    {$IFDEF UNIX}POpen(Cor_file,'smooth_GC_v2.py '+ChangeFileExt(jflib_name, '.txt'),'R'); {$ENDIF}
    for I := 0 to 400 do
    begin
      Read(Cor_file, Cor_dp);
      binarr[I]:=Cor_dp;
    end;
    {$IFDEF UNIX}PClose(Cor_file);  {$ENDIF}
    WriteLN('Lowess smoothing completed in '+TimeToStr(Now-Origin_time));

    //Apply correction and save data
    Origin_time:=Now;
    for I:=0 to GC_size-1 do
    begin
      GC_bin:=Round(GC[I]*4);
      Cor_dp:=binarr[GC_bin]*jf_count[I];

      //Save corrected value into GC array
      GC[I]:=Cor_dp;
    end;
    WriteLN('GC corrected in '+TimeToStr(Now-Origin_time));

    //Free memory and save file
    SetLength(jf_count,0);

    Origin_time:=Now;
    AssignFile(GC_file,ChangeFileExt(jflib_name, '_result.bin'));
    FileMode := fmOpenWrite;
    Rewrite(GC_file);
    Reset(GC_file);
    I:=0;
    repeat
      if GC_size-I >= 131072 then
        BlockWrite(GC_file,GC[I],131072,Read_size)
      else
        BlockWrite(GC_file,GC[i],GC_size-I,Read_size);
      Inc(I,Read_size);
    until I=GC_size;
    CloseFile(GC_file);
    WriteLN('File written to disk in '+TimeToStr(Now-Origin_time));
  finally
    SetLength(GC,0);
    SetLength(jf_count,0);
    //CN2_flag.Free;
  end;
  // stop program loop
  Terminate;
end;

constructor TKmerPipeline.Create(TheOwner: TComponent);
begin
  inherited Create(TheOwner);
  StopOnException:=True;
end;

destructor TKmerPipeline.Destroy;
begin
  inherited Destroy;
end;

procedure TKmerPipeline.WriteHelp;
begin
  { add your help code here }
  writeln('Usage: ',ExeName,' -h');
end;

var
  Application: TKmerPipeline;
begin
  Application:=TKmerPipeline.Create(nil);
  Application.Title:='Kmer Pipeline';
  Application.Run;
  Application.Free;
end.

