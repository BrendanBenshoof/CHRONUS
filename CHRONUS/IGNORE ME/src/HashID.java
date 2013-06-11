
import  java.math.BigInteger;

import com.sun.org.apache.xml.internal.security.utils.Base64;


public class HashID implements Comparable<HashID>{
	private BigInteger myID;
	
	public HashID(BigInteger hashval) {
		// TODO Auto-generated constructor stub
		myID = hashval;
	}

	@Override
	public int compareTo(HashID B) {
		// TODO Auto-generated method stub
		return myID.compareTo(B.getBigInt());
	}
	
	//Distance from A to B. If B is numerically less then A, it calculates distance around the origin
	public BigInteger getDistance(HashID B)
	{
		BigInteger MAX = HashGenerator.getInstance().GetMax_HASHID();
		BigInteger val = B.getBigInt().subtract(myID);
		if(val.compareTo(BigInteger.ZERO)==-1){
			val = MAX.add(val);
		}
		
		return val;
		
	}
	
	
	public BigInteger getBigInt()
	{
		return myID;
	}
	
	public String toString()
	{
		return Base64.encode(myID);		
	}
}
