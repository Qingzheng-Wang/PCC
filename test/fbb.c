int main(){
    int arr[25];
    int index = 0;
    // �󣰡�������쳲���������
    arr[0] = 1;
    arr[1] = 2;
    arr[2] = 3;
    while(index < 10*2 ){
        int b = arr[index];
        arr[index+2]=arr[index+1] + b;
        index = index +1;
    }
}