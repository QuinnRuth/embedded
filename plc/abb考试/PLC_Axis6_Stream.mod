MODULE PLC_Axis6_Stream

    ! === 参数：按你的PLC改这里 ===
    PERS string gPlcIp := "192.168.0.1";
    PERS num    gPlcPort := 2000;
    PERS num    gSendPeriod := 0.2;   ! 秒：0.1~0.3 都可以

    VAR socketdev gSock;
    VAR bool gSockOpen := FALSE;

    VAR intnum gIntNo;

    VAR num gAxis{6};
    VAR rawbytes gRaw;
    VAR byte gTmp{4};
    VAR byte gFrame{24};

    PROC BuildFrame()
        VAR jointtarget jt;
        VAR num i;
        VAR num p;

        jt := CJointT();

        gAxis{1} := jt.robax.rax_1;
        gAxis{2} := jt.robax.rax_2;
        gAxis{3} := jt.robax.rax_3;
        gAxis{4} := jt.robax.rax_4;
        gAxis{5} := jt.robax.rax_5;
        gAxis{6} := jt.robax.rax_6;

        ClearRawBytes gRaw;
        p := 1;

        FOR i FROM 1 TO 6 DO
            PackRawBytes gAxis{i}, gRaw, 1\Float4;

            UnpackRawBytes gRaw, 1, gTmp{1}\Hex1;
            UnpackRawBytes gRaw, 2, gTmp{2}\Hex1;
            UnpackRawBytes gRaw, 3, gTmp{3}\Hex1;
            UnpackRawBytes gRaw, 4, gTmp{4}\Hex1;

            ! 按参考做反序（大端网络序）
            gFrame{p} := gTmp{4}; p := p + 1;
            gFrame{p} := gTmp{3}; p := p + 1;
            gFrame{p} := gTmp{2}; p := p + 1;
            gFrame{p} := gTmp{1}; p := p + 1;
        ENDFOR
    ENDPROC

    PROC EnsureConnected()
        IF gSockOpen THEN
            RETURN;
        ENDIF

        SocketClose gSock;
        SocketCreate gSock;
        SocketConnect gSock, gPlcIp, gPlcPort;
        gSockOpen := TRUE;

    ERROR
        gSockOpen := FALSE;
        TRYNEXT;
    ENDPROC

    PROC SendFrame()
        EnsureConnected;

        IF NOT gSockOpen THEN
            RETURN;
        ENDIF

        SocketSend gSock\data:=gFrame;

    ERROR
        gSockOpen := FALSE;
        SocketClose gSock;
        TRYNEXT;
    ENDPROC

    PROC main()
        WHILE TRUE DO
            BuildFrame;
            SendFrame;
            WaitTime gSendPeriod;
        ENDWHILE
    ENDPROC

ENDMODULE
