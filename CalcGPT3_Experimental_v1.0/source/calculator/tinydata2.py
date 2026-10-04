# CalcGPT 3 model installer 2 of 8. Run in order.
MODEL_ID=1282619148
BUILD=2
from ti_system import store_list,recall_list
FORMAT=13
ALPHABET="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{|}~"
def decode(blob,length):
 out=[]
 for start in range(0,len(blob),5):
  value=0
  for ch in blob[start:start+5]: value=value*85+ALPHABET.index(ch)
  out.extend(((value>>24)&255,(value>>16)&255,(value>>8)&255,value&255))
 return out[:length]
def checksum(values):
 a=1; b=0
 for value in values:
  a=(a+value)%65521
  b=(b+a)%65521
 return (b<<16)|a
def installed(stage):
 try: marker=recall_list("tds"+str(stage))
 except Exception: return False
 return len(marker)>0 and int(marker[0])==MODEL_ID
def install(name,length,signed,blob,expect):
 values=decode(blob,length)
 if checksum(values)!=expect:
  print("Checksum failed for",name,"- re-paste this program"); raise SystemExit
 if signed:
  for j in range(len(values)):
   if values[j]>127: values[j]-=256
  pairs=[]
  for j in range(0,len(values),2):
   first=values[j]+128
   second=values[j+1]+128 if j+1<len(values) else 128
   pairs.append(first*256+second)
  values=pairs
 store_list(name,values)
 if len(recall_list(name))!=len(values):
  print("Verification failed for",name,"- re-paste this program"); raise SystemExit
def verify(prefix,count,length,expect):
 a=1; b=0; seen=0
 for part in range(count):
  for packed in recall_list(prefix+str(part)):
   packed=int(packed)
   for value in ((((packed>>8)-128)&255),(((packed&255)-128)&255)):
    if seen>=length: break
    a=(a+value)%65521
    b=(b+a)%65521
    seen+=1
 if seen!=length:
  print("Incomplete model part",prefix); raise SystemExit
 if (b<<16)|a!=expect:
  print("Corrupt model part",prefix); raise SystemExit

if installed(2):
 print("Part 2 of 8 already installed; skipping.")
 raise SystemExit
install('tdq0x5',1600,1,'_~ro$?+^*^{QT<d`VSKV9rNDs3i=!T6$ljd9r+Lo?+p3_5a0j!0tfye3E}w*2m1^P2<q+R^BLX(0qOkx_ZJWR3-99d2^|Oq0PN-W2J77q{uTrsEAsgS0}S#300#dA{`?353FjFB0vG-B8V~mi8u0o2-}&Gc%E{^7#_Z)34+a=B4Im5l{r4023ibm04Fm87{SN*85g!W!0qp`3`uqL{0Tv7N4+IA65e4tw_UQTm4D|*D1@!Uu9sBeN0RZ?F7WMG`2Gjfr`QiKi83PC71_THO6XzHa5Zo6E_wx$u2^I_Y@e1bP5b@{z5Z?&<+0^9w2n5&r^z8cJA^rvj0Q?&K3H9mi;UgCe01w>x4ebRA^!ykZ`1k@71@-$00t5B_9Rmg^`ttbr^ziuC`yKWF9RTqOApG|f4+{za^!5e!_x}1H{thG#_V4-w_w_gk@d*b85)b<M8zuPo)C3VF?-Km<4d?X@{T40x^6vfO3JV_b1_tc#3DOG=1sV?a=Mnx3AL{q*@E0H${O<-F5B=o%4glow^W+T`00#*H3hoL984mCN`v40T4(|p8<>Jx>4*w+h3fLa-4E+WC0{Qd=2@4Yi|Nr<W+ZzHP^Wyvn6Z-=I1@RFC3HS8~3-=TE6aDoS=HwIu`t=Ln?d|gS1|0w%2>=QI{p}h22=@U02>kC96BP#l{}Tuu3hE2_+rSp;CH49R4;AO<`t<w=*Z%|)_XZmS0qhh7126yl%meo7>IeD^>iZYv_2>)?009pm=pY6790&gr0{0c_7Z2_89`F$H90>Xz_YDyn=J5*40qyhv(IYJ)!U78a7~ll-?C#<H>mA?g9~lA)B?Auz4Ef>x`~U|G5BKBZ9T4sc{r~|GE++Zy?HU9U?+W4o0zdE$<OUcC5bq7~{2~VM7Ut##2@VVb`t#%m_UH!c?DGlr4FmB2?*85J3oQ8<@&^0}0Q?RJ3jE&_5BLrR783#y?ho+f>;n1(`~La#7V!8F3K`c1{1hMS(HZ~H{}~?%5CSXv*aY_#@c{4!6Z-=H2j&0?7Xs-0_Y3+V@f7t78WbS|7x(%4C;IX2A?o-C2<`(i#RvQb@&yMi8!j0b2K>V000RaJ?cV<T@a6Ic7!VN(F8BuSGVJLH58W0W9o_90_!jcb2Ne+K`|S4S67%~E4F&%A6d&mL4;K*?1J?HN`VbKU@CEh%9P#%E3mo_w_#pNY@$>>6BK_eQ=nM7;4h<eE_1gpi^d<=4{p0H0^Y{Y=6$jh#^w$Ij_7MEv=mHG$3H&4V=JyZ?-w+M(=<^F3Dev<W?eQ1~6A#%c4+7{9_xl$R{MrBg|NQ~>Ar}J&+7bi-?Bo~v`{w%t`V$T!{}v1H2m=ih;`RLxIPLu#`U@)(04VtL?)m;42l5^B{`w3H5%>oT0`u|=@YDqS{Q4U50R92>8UXL}2M_-O8RPyS5bPK9{plYW+9mh}+w=tjBh=sM?G^+973AUn{viJp2lwgw2lEjD`Rx(n_U7{p^8)hq3Kk#o1?~A10P_V1`2ykm7Wo(h90C0R>iYr+^!*_04f6U57YzpZ5$){_3-AgE?BXT-2<iF!4gCcR`w8p}`0(T#;QI3s@%IG#9|-#z2@m%Y{l^>f*6|Dc4Cmzp0So&L_yGO-`RVQu+5is-1OWa45<U$P4h{426$$bF><9Gn)ba1<_Z83d^feIs@&Nt#0@euy3j6r(CKmAp3-|g0G8PF1+z;gr4Dtab7#9Ej0OJ4L?%e6!3lRq99trOF2OJpe{TlS#<@WOg=I`?!7X0u44;dB<74Y};784U94F={IECA;L>=F#|2Myx<_WSbm-1-Id2Jh<-3hn^?`w#O26XW^-6VU7S|KQ;l_5ld>7ZCXcCGXz?^~MwjB>v$O7xV}0_xKC*7W(ZL+xH3+3HSj3{O$Vx4+`k=0}Try>gM|z7z+ss?;ij52Pf_i4G-`s=mY-y5A^sIF#Q(o3H<UH|M1fS<q;6>`P>v00V)#N4if?U2=n?D^8E|-_W#rm{0jpp2ND7u@%`od=J*fn_3r)sHzyG&_8%Yr',4153739859)
install('tdq0x6',1600,1,'0Sycb$nXgj1s?<s2@UV@3MUOfDccbFAM_RQ2kZL?9Q5Y-3hMm^`uY?y?gAMnDexHm0rm9*7UjVP6!!`N<oWFd7WxSk2Lk->0P5!D_uLT>?(Gfy1^njy5f%Xi0R#8{2G#}m=?D__`VrXr?JWNn5hm;q`~Dyh^!5tp5$M?d82b+z=O!KjBmDIP@81Ic3H<;25BU$|2>b8i4Bzq$?F!}j2+#2F5d;R`91a2u4f*yO?eh`<1KRWg{t^TR6cGLI5B38f{Q(mX83OO{00tWe0rma^65;#&3K1RZ9P9rB{U#C?3i09n1rGES@e2#xAMWk?5)lyb00;LX4frPZ>>Ah8`5h7d815qw-UtH?2Kxv6_uvr|2k`X;AoSe~1<?2f3iufT_V_Uc1QO>J8xHjT6a@74|M?6Q@Ad!R8TsM};UEe6{S*G!|M&k7@cjnn5KAHK?kLmv1P34A?dshe1RVw<C-vwc5c}~H@&?`H3+CGf@B-xO3-{~;4HDAp82%6}9~<)&>HHee<@DY2{t@)(-WC2C5d;tX@C*(70sHXz^bi;W=KuKh`{ED&0`Kb<{`va;9sURi2ma#&`S<<^{`3L$5BK2b_zva;`VkQ9*WvjB@dE%9Dc|x102TQQ{0sL44in%90Syc81pnL$=n(Gu5a9OmC-wvN@dX<J1@rj#5(WwO1PuHQ4b}e?0}%uR0{!Fx0z3>5^a}0#?%M_b4(|!-^5zW+84L3h{S6ck=K>7W2@&W1?)vBu5);z@_7Mo};px~2{{I{V?)U@#2Lba5^$QsI75exO>iq)g{`l(V^z!fk|M>P95bF&G_ZR~S0O`{J01EyM9OCr%1NIg=_wn}l`s?%nED#6c^a$V-4e$5q^!yt3`2`6L;1m4<2+{r<6X*pC?+5cR6#?}4_7n#i3HSvH2@LrL-vKcg3jzTM87v;lChq|H;o$@g`s)$;_Wb?!8Taf6842zA3jho65$g8w9p~%`4FLxK{UPup^!gDl=l2}+1`-MC?*8BV1N-nW`v&v$`}P<T0Q>#+BK`&c0{!&@1rGEH`tu9@1MBqv1{V<K-q{=S8xQXb_wEY@{O|wg9SR8g5BT&H@%r=%2<Hn54h-`93^V!f^&SKQ{P+(c@dWh*_~zIY689Mp`}X+e^7Q)^1ql)M3HbT>4habV1q1^S0@DHm>fHnz4({vs|NQ*{3jX*2;^OuY`xzMm_XXwm4F>fN02c5a`wjvN`}G7V1M>I-B>fZw5%&Wh_wxT7{PpSu^7teK^&$QG@caS#1M(>b{PyuF1@Q*>9Vhwu^bW<^4*CiG=Hd3!_VfB10Tt@+C-U*(F&X?M?+g+T6aVS-6!Z5A6X56ZCJhHK@9O*i7X9rF4)^i;4({Fq?*#N80{9U0{2uM_5e^d-^&uep@ACr?{Q)5T1@ZR^5D*On`WO2R==Adf`26+l_}Kmd7VYf}<o^C41Ln#Jx$Nc^_7?K@?+EA%2oD_*<rfAQ;|B2>5dHNP^9udx5BK&B_2?21_WA|?76SD0`U4T>6$k?h@%s%L{qg+}3H0vf?)d%%9{=zF+XVOv000;M_~`%)0Sx^F`X3eh2@eP+4FnnZ_`nC|1NR*J9PI}P`27nT_469>4etE@5Bw7S00RL1^8NG*@BI_;|MB7a3I_ZY4F>}T2leq5_5Km^2Iuzu3;Gca@dy(55C8K61_l)X^YaGi67~!K^bq#@1n&A5+wS)p@bfhL<reV={Q(T+3*7$y3=9L|`}g!44E7rD4*m5O@$3o;?*aYd1sLrC4Gszw@fHp33fklouk-&8`vwK%;Q;IT1PBfc(e&*76%`ZC>=6b4A1w|MEbT28|MmX}0}l)b=lS^gApqj|6dCaR^#cL}>Jt4P0P6+w4Gb0e3IpQs-2@sJ<plor1_bC5;uh8Y111Lw0nHj1@(K~@{Pg4I0S^EJ3IfsSB?9yb1pxu@2?F#JCFK4584BhN`{DBX@%b9)5%&J;@%I4_;|}@_3gQU<?fD4@1Oo5^9ti6I<{JzU@bvi__WSbx>eS@{DiZbj1Pa>|',2249072558)
install('tdq0x7',1600,1,'4$TPh0}U4z>iPH^BpuP(CItoS+~VL*@a!ZU(eEAX5)S<e?ECo${SFf<?*#T0D)s&V_Zj^91P|^K`SLFjALZ=w0?+9A{SE^L0ps%a7!Us%-}Vdw`S|?={qqC-?*j@9_WbP?^7|L|<q7-VA{p@!3JUrg1k?Tl`vCe6^Zerb6aWJg5Ca7Q1@9dV7Vr!W4EPcG3=Izg`UCLo66N;t_Y4g65bgc;59kc;8Q}W_^%^4*?F;<>#r^97{r3<9Ao=^n><Ril1^yoqAPEi#11KB=0Sx-^^cxo-85#Es9~cY%4igaK`|9c6_V(lp4eJ&A`ttbn9{d9T1`X%*^!oN0>=NV*8{!S;=>P!j5cBctG56j9{rUnC2krpx1rh=f1@-V2<`5495zz_(=LY-}155!F^9TOh>j3Kp`~v>#3*-X~_4@<%@(~9R{MHE>{rLq6{|^cc`TPR&{O$wu|NHR>@ev&g0Q=wm^AjEg5eeY_{sHd)_Sy*l_xcU+68ZiTCj|8UE7kh^?HB(C^8Nq%=kgI51u5tJ0No83^7!Zy0Nv~i0S^Kb2M_!q2i@xm@BR1f1mXey_5S+q2mAjQ_Wu+e{rnv60{HC%4-5bZ`TZ97@6_oQ?Ck#-_TKp+8Wafq1pEyE4F2;T4BQ$E`|v6H^cVF31O(_60TlB8#nTzP?B@0R4IKS9;qCzm2O9q+>;(bp^Zoh=0|Elp2o)15{1D*t1_uu3*y;NG7zOy=`Q{(*CB^a;>IDGu@7fL%1pnjx=?)hJ>FnPa{Q?US3jYWI86ETv`5g-R01XWJ<JtZV3H$l`82RfA8S2yrixVRJAosru+W_nH1@iGDF5JTP`PuFL7Utm}DDD0f`V9^C3H}2M^b`js@c}Is^X2Rg9Ul$f69w)11_S>F01zej00t)y4gdHY7#{EG|L6P#5%l;5=IiS9G5Y`d1SRt4DCGzj<L)T)01fd33H=BZDFgQU^ziQZ5d8|*@bwSt?;rZs83qUY`ve~P{~iqa0RRgP?+XM00^tPd@(TV1^XnJ$_W=9&5(EU}9`H391=0o_4g3TT`1A1h5cmKW7z_LZ8uI@H2l?SC7Wv5z0Pz^%>Ko<L4E+B4{pcY7^$z#|4g3uO2m|Ey2D#)8_VfH966xpx0`U?N?dsC*2?zNP*zW@n`3D&d^Azk4^9SxAJuMO85e*av^VI0)3K#?qCim&|9QO1C+W#IJ0RZCy4fON}{`uzy4*v=i;|LKU0QK)cF82TI5(MP$`TqtD{|^QR3h3+j{{Qdz1r+l673u8*5V_YM)9&5;8v*+W@B0D~_6_+G;{yT}2L$i+_y!2+2@3!j7~cUF=m8q{^a$eVEd>Sy2oLxU4Gi4_6aEG+|LpV!5%~T14E5#o1pXu=`3djp1_}EE=pz9D`wROADFp-;>Gt;l1`7V{9s2(D2=(yw8wc?R{R-&@>kQ-~@(LF21uO;(2M-nx-v{J49~lZM4JZfv_~_~c_~ZE#`uPq35BTu&2ptIh5fb_O>HiiC@AKsM0{+?j_5CFN0t5jr1=|nu90J_-4dC|g{vjD5@aOXp0pSn${re3f9|Z>v`1b$@1LOkv0iz5q$`#|z=>g99{qpMg7YX?H{}=%x_6+Y03f}PX`X>3<4fpvk`tAP#4D8wq2=wY0BJ}V12lNvj{Pqts6zL%Y^!^nJ01yEe@CWJ``r`!T>iiY^@b>Te8x0Es6#NGQ3d{cY0SyQd{{!0i=>`!99~tup==atwKkOU!>;x7M%^2YU4hss=0N@A_>+}cv67b*u01OKX_Z<ZC?(pz1>g@*W6YI+h2>AjGB^?Cl8R!P@2mb#3`TPCxCkFul9PR}eAH*3c?$I;z{{{^RClAma*eU5A4%;051nLbE{}Txn4;L2k2?-Dp9ozOG`|%{|_onwP`UUsbB_uo)`uqVU5B>cG-xUn&@74ee{_z9j2MgsA3-tR85E}>p9r^6>3I*&9<>vPT`TGp-^xoF&^ZF|a3JvV%9|rXe<oOB+^Xc~b2P6dp_5SAt{O=F~6!r)D2K40l0R0O34I}dq',3565228502)
install('tdq1x0',1600,1,'@izwV5b@x;8utJPANTdf5B%=?`4aE)0O2)V`~~d@Gz;9(9suYR2-^eT?CJRz_}TOW2M8<E_#7Vw3hCag2ovzw`u)%f?HAla57;;i?j-QsIS3x`0}2ce|NaZ)@(Iu&*#RpA`t{)Y3<}2n+}Yv*3+eU^2Jq@CBI4TS0|Y$@Lh1p(_7Mi|`ybZj-ukZsz!D)qEz<}I^Yz*0`wZdt<{J+01Ut~{>C@EsBGbqO`0gV!+|~po@HFq`62I`<2OaiZ=Iz`42JZmu81Mb#AI1Fq5cUD^0R-gY61f`t9Od@n_uvQk4;SPi;|$orLki9vWI+4q-2v$5B_Q_%_D~=L8WH~W6>1y<5hUOu^xYBo<17sd5cudP4h0zX1K{Z&902L+2k0FnA?OnP?+O<gA@dv&7Y+U0Bj^J47v|_285-{SF#Q^vDg*ug^s?sE^z!O|3l$6!4Fmq*JK@wb1{ewf4JRD$H17BqFbu;3+Y$~21_kUE4+ie$C;1ln8xQse4+RGNDi`m{<mDz800j#O!uR3f747gH@aQk=+V21p8~Yy&BF*~G3Kj1O1PtQ}*8LCi;@=A40KV0`^v3E3`}*hy(JB)#D*X5sGV2c%8ZF@N_uwND75(}J{Rrw4@(~Tw<lz_<@Bab{_4Vk}Au<g1{4Z0`77+F%2pZHDB>f8UAlvI5>C@of==@zGJ^%PO>hbmED(&432Lk&Q9|Il83+doN{s{jN2M7=1OYPAK9V6l!_YC+R%MbA!A_W*1DB<h#=`HRC<^ulo2sQZX0QVjE9roSi91a2CDIod@JPHBRDD4^GAi?L|+#28K5$g`r0vjF^bkZ&mEW-{V9`YB~BQgag@*wpk84&^x|HbtN_yPOr>J{+v6AA6^@BJC-4B;Ht6ZRYH5C$9FD+bc(7YgL*{O&Ev*XR26;S??W4MOiSC*t?{2($V$-}5Q)4h}g2(Fye#LfiD{D+TEk8zK0^y6y=a8V3px8Sxk@@Xs#b#?2V&1;;=51o_nr_UQ53DwYTh{}cDt7ZWtl)<h%zC>l%FDc1GhH6jJ`5Frlr3DxE_Ebs~E4c`p%(dOdn;T;Gj5hwZj^8XL&ALbnT{q-ZU`VtfU5y%=k3LN8C|M>3N^(_^?69NmkDnr^E3<nqFB*o_bDM1eB@b&@y2@we+7ZCpe3c>>x_b&X~<NplH?g8}>AKn=52H7184;}c-F7w?5HU=Ry8Yuk)IoR|AY#{9+IpsAL9~lM+1Nau#75N?X3HI>I0Rs382m|`{6ZQ!E5C;4S1Oo&87yKpX7W)1|@(&sCCd3L59XlJ#@&W7B<pkq30v8|%Fs={!8~`Hf5(*Uj3hM;(I`|djFVy+><Nh4^^yxSLG%^1Z^%4u&62$T(EBXcODE%Ym=<WsA?fu;m56I>-0pKtB82%0m3nTdkAmsY@2>a6)93Ki3-Un{fE#=@YNgYBWA*TKb{@>rW=JXFpHR={92<%1k`qd=#Nb|=I5EKC4AOQUg81nn`82T9*{~ZIx^cM037%2ubHVPc@3F8&)AqD;I04f#i5D)X{)d&Fn1?=VJ3h@o|{{#~H^#LIo*XIE#2M+M+9V7?vB=Z)+{tyP~91QdJN#rvG7a0s7-uVRB4D1c;@a5^__8tZ>9^DlU8~-Wz2?6xt7V_aE1nCRv{T1s$3J&q=2L2id1Pt;5{RkEB^$7X<6Wj<S>EIXq-~=TI6BzN^^(yHD>DetB==#|T2-@(!7Zw5aB^U7F6#&@p2I42`1^ewQD(dABMi|@m5&aqy%JCT)1NGMb1QP-2-0k%*7!)1t@f+tC&=WEc-sjWyH`ekO76kI^FVFi5_x0`w2^R+l+U(x(`vLa@5#s~|GdtTA{ul8L2n`kr?(YT&2o?z@63Y4R><tq890LCu-wf{f+~w>7;|vAj+2$w?^B))(9ts5h`2X(w4-N6?`t$1M5)SAM>Ln!k_5%&zA|wA0A?x!V=^_>V+QK9D#}fPT0TU4m<^&z${O;!%<I?B}BNYkpCh86L5l+JJ-vSox0RaL6000000sH{|0sj940RsO3',801374458)
install('tdq1x1',200,1,'C-C+B^c4>22LBWg)D!|77vk{y6Wsm*2qG=({Sfo><M#Xu@(2U%4*BQ**y0xG2nF@w{OtSw-t_qb;}zQl><=&h3)tHi8vhLR7v0nK1O5a43h*ce1n>R)6y)$A{tEdI1^WF3{S5~c0QLF$1qk;64E`4U?Gh#9_8##N5(o(I{{<u?Asn&-&HWqcHTe4D|1%{1_3az?_VL6KC=VLI=L+f@AnXqU`u7>(-2@KD7!?Z&_#M~x{{#~c5c&)U0}AZn',1164011153)
store_list("tds2",[MODEL_ID])
print("Part 2 of 8 installed. Run tinydata3 next.")
