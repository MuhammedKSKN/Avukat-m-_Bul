#include <stdio.h>
#include <stdlib.h>

//interval yapısını tanımlayım
typedef struct{
    int start;
    int end;
    int index;//orijinal sıralmaayı takip için
}Interval;

//karşılaştırma fonksiyonu intervalların bitiş zamanlarına göre sıralama
int compare (const void *a ,const void *b){
    Interval *intervalA=(Interval *)a;
    Interval *intervalB=(Interval *)b;
    return intervalA->end-intervalB->end;

}
//interval shudeling algıritması 
void intervalSchuduling(Interval intervals[],int n){
    //intervalları bitiş zamanına göre sıralama
    qsort(intervals,n,sizeof(Interval),compare);

    printf("secilen isler:\n");

    int lastSelectedEnd=0;

    for (int i =0;i<n;i++){
        if(intervals[i].start>=lastSelectedEnd){
            //iş seçildi
            printf("iş %d:Başlangıç=%d, Bitiş=%d\n",intervals[i].start,intervals[i].end);
            lastSelectedEnd =intervals[i].end;//seçilen işin bitiş zamanını güncelle
        }
    }
}
int main(){
    int n;
    printf("Toplam iş sayısını girin :");
    scanf("%d",&n);
    Interval intervals[n];
    printf("Her isin başlangıç ve bitiş zamanını gitin\n");
    for(int i =0;i<n;i++){
        printf("İş %d \n",i+1);
        printf("Başlangıç:");
        scanf("%d",&intervals[i].start);
        printf("Bitiş:");
        scanf("%d",&intervals[i].end);
        intervals[i].index=i+1;//iş numarasını sakla

    }
    intervalSchuduling(intervals,n);
    return 0;


}
//toplam 12 dersi 4 farklı dersliğe 8-17 arasına yerleştiren kodu yazınız. Ders saatleri en az 2 saat olacak
//interval partition problem aralık bölümlendirme problemi 
//yeni soru 3 sınıf 7 ders ders saatleri en az 3 saat 