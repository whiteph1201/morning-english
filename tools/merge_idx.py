"""python3 merge_idx.py <출력폴더> : idxNN.json 들을 idx.json 하나로 합치고 조각 파일은 지운다."""
import sys,json,glob,os,re
out=sys.argv[1];allx={}
for f in sorted(glob.glob(out+'/idx[0-9][0-9].json')):
    allx[str(int(re.search(r'idx(\d+)',f).group(1)))]=json.load(open(f));os.remove(f)
json.dump(allx,open(out+'/idx.json','w'),ensure_ascii=False,separators=(',',':'))
print(len(allx),'days')
