int main(){
int i = 0;
while(i < 10){
    i = i + 1;
}
}
/*
(=,0,0,i)
(block,0,0,W1)
(j<,i,10,begin3)
(j,0,0,end3)
(block,0,0,begin3)
(+,i,1,T0)
(=,T0,0,i)
(j,0,0,W1)
(block,0,0,end3)
*/