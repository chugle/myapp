program caishuzi;
var
	i,j,k,a,b:integer;
	daan,shuru:array[1..4] of integer;shuzi:array[0..9] of integer;

begin
{产生随机数}
	randomize();
	for i:=1 to 4 do
	begin
		daan[i]:=random(9);
		while shuzi[daan[i]]=1 do 
			daan[i]:=random(9);
		shuzi[daan[i]]:=1;
	end;
	
	
{	for i:=1 to 4 do
		write(daan[i]:2);
	writeln;}
	
{输入10组数字，判断情况}
	for i:=1 to 10 do
	begin
		a:=0;b:=0;
		for j:= 1 to 4 do
		begin
			read(shuru[j]);
			if shuru[j]=daan[j] then
				inc(a)
			else
				for k:=1 to 4 do
				begin
					if shuru[j]=daan[k] then
						inc(b);
				end;
			
		end;
		if a=4 then 
		begin
			write('great,you are right!');
			break;
		end
		else
			writeln(a,'a,',b,'b');
	end;		
	if i=10 then
		begin
			write('you are so weak,the answer is:');
			for i:=1 to 4 do
				write(daan[i]:2);
			writeln;
		end;
	readln(a);	
end.
	