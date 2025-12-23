# ABB机器人发送当前位置坐标给PLC

ABB机器人发送当前位置坐标给PLC,附机器人端源码！

![](https://mmbiz.qpic.cn/sz_mmbiz_png/qMAl0dc6o3OF23Z1iaFQib30Fa9icibhVqWNYh2icSgaA76JV7DVIHobgC2ScrPweUWSTsd7T6FKS69tSibIibhXtJibVg/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/qMAl0dc6o3OF23Z1iaFQib30Fa9icibhVqWNV1ia7tpapqSUicuibicEgdP3SoMojEpa2vskb9nhAexLFUPlicibYpNTibnQg/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/qMAl0dc6o3OF23Z1iaFQib30Fa9icibhVqWNia9BAqG5icUecLk6gjhGkoV0wIeDwHsUK5PcEMsO9v8Qib3q2oiaias6KYg/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/qMAl0dc6o3OF23Z1iaFQib30Fa9icibhVqWNwv2PQnP62x3beuQGsBINeOnloZBDfzz4MgJibrQavibAtfobxdzAiagrw/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/qMAl0dc6o3OF23Z1iaFQib30Fa9icibhVqWNNhIfOhgLNW1WibPOMRPz2M08GShic2dqNticvickX94E3MCuLoic699f7Hg/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/qMAl0dc6o3OF23Z1iaFQib30Fa9icibhVqWNNmRva2tcLeQJJiaj9xiaJXAibVwdGgpNtZMxZgqDot7kUgJnOywX38Qdw/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/qMAl0dc6o3OF23Z1iaFQib30Fa9icibhVqWNOjzj3odoAfINhoS0icXljwluwKK1kXvDZ4cmvGyVKUVfWPAfO94lz0A/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/qMAl0dc6o3OF23Z1iaFQib30Fa9icibhVqWNwiaHqKt858GHicdQW3FIjhichBYCcR1Q7zTmxupMiakdORIbuvbnVibqibDg/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/qMAl0dc6o3OF23Z1iaFQib30Fa9icibhVqWNSJogvMGwnqJNqcWic3HfDXCBuicpsTAQbRFDuwgIibjJKE2ZzX4QszoZQ/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/qMAl0dc6o3OF23Z1iaFQib30Fa9icibhVqWNRzS9XtAx9kbmMItB0376nhNbeU65KeX69pgJDIDOHSJZ2dj3rKyrOQ/640?wx_fmt=png)

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   * 

    
    
    MODULE SUCC_B_station_Lmsa!B站林木森Lmsa    VAR intnum intno1; !声明一个中断识别号    VAR num POS{9};    !声明一个存放J1-J6 XYZ坐标的数组    VAR rawbytes rawbyte1; !声明一个Rabytes数据类型用于存放打包与解包的数据。    VAR byte byte1{4};  !声明存放一个浮点数数据被拆分成组成这个浮点数的4个字节数据。  
        VAR byte Position{36};!存放将9个坐标浮点数转换为字节的4X9=36字节的一个数组“Position{36}”    VAR num Lmsa; !声明一个遍历Position数组的NUM变量    CONST jointtarget Phome{8}:=[[[90,-20,-57.2,-0.59,90,0.2584],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]],[[-7.85711E-7,7.00837,-7.39141,1.05234E-39,30.3831,1.45085E-37],[9E+9,9E+9,9E+9,9E+9,9E+9,9E+9]],[[4.50332,7.23671,-7.64511,-7.65159,30.7097,8.8439],[9E+9,9E+9,9E+9,9E+9,9E+9,9E+9]],[[-16.693,8.55096,-1.39327,32.3497,27.7035,-37.8103],[9E+9,9E+9,9E+9,9E+9,9E+9,9E+9]],[[-10.9289,-32.9271,32.5103,18.0069,32.1168,-20.9049],[9E+9,9E+9,9E+9,9E+9,9E+9,9E+9]],[[-36.0406,32.8987,-33.2878,45.3095,45.8053,-55.1465],[9E+9,9E+9,9E+9,9E+9,9E+9,9E+9]],[[-36.0406,60.5635,-0.919765,124.632,38.277,-151.317],[9E+9,9E+9,9E+9,9E+9,9E+9,9E+9]],[[-36.0406,37.4155,-47.9823,39.4339,-1.33303,-46.1254],[9E+9,9E+9,9E+9,9E+9,9E+9,9E+9]]];  
        PROC Position_Lmsa() !读取机器人当前位置的子程序  
            VAR jointtarget Jpos; !声明jointtarget用于存放机器人关节轴角度数据        VAR robtarget Lpos;  !声明robtarget用于存放机器人XYZ数据        Jpos:=CJointT();     !读取机器人当前位置6个关节轴角度存入Jpos        Pos{1}:=Jpos.robax.rax_1; !把机器人1轴角度的数据放入到Pos{1}中        Pos{2}:=Jpos.robax.rax_2;        Pos{3}:=Jpos.robax.rax_3;        Pos{4}:=Jpos.robax.rax_4;        Pos{5}:=Jpos.robax.rax_5;        Pos{6}:=Jpos.robax.rax_6;!把机器人6轴角度的数据放入到Pos{6}中        Lpos:=CRobT();     !读取机器人当前位置的坐标存入Lpos        Pos{7}:=Lpos.trans.x; !把机器人X轴坐标的数据放入到Pos{7}中        Pos{8}:=Lpos.trans.y; !把机器人X轴坐标的数据放入到Pos{8}中        Pos{9}:=Lpos.trans.z; !把机器人Z轴坐标的数据放入到Pos{9}中  
            ClearRawBytes rawbyte1; !清除Rwabyte1中的值        Lmsa:=1;   !初始化Lmsa,用于从下标1开始遍历Position这个数组        FOR I FROM 1 TO 9 DO  !开始9次循环            PackRawBytes POS{I},rawbyte1,1\Float4;  !把Pos{i}的值以浮点数的形式打包放入到Rwabyte1中            FOR J FROM 1 TO 4 DO !开始4次循环                UnpackRawBytes rawbyte1,J,byte1{J}\hex1;!把rawbyte1中的值拆分成四个字节以16进制的形式放入到Byte1数组的四个元素中            ENDFOR  !结束4次循环            FOR K FROM 4 TO 1 DO  !开始4次循环                Position{Lmsa}:=byte1{k};!把byte1数组中的元素从大到小赋值给Posittion数组                Incr Lmsa;!Lmsa 变量自增1             ENDFOR!结束4次循环        ENDFOR!结束9次循环    ENDPROC  
        Proc Send_Pos()        SocketClose Socket1;        SocketCreate Socket1;        SocketConnect Socket1,"192.168.0.1",2000;        SocketSend Socket1\data:=Position;        SocketClose Socket1;    ENDPROC  
        PROC main()!主程序        IDelete intno1; !删除一个中断识别号        CONNECT intno1 WITH HuiChuan_Lmsa; !把Huichuan_Lmsa这个程序关联在Intno1的中断识别号上        ITimer 0.8,intno1; !每0.8秒执行一次HuiChuan_Lmsa程序        FOR i FROM 1 TO 8 DO            for j from 1 to 8 DO                MoveAbsJ phome{j},v500,z30,tool0;                waittime 2;            ENDFOR        ENDFOR    ENDPROC  
        TRAP HuiChuan_Lmsa !中断程序        Position_Lmsa; !调用Position_Lmsa        Send_Pos; !调用Send_Pos    ENDTRAP !结束中断  
    ENDMODULE

  

