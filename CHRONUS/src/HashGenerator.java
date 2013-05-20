import java.math.BigInteger;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;


public class HashGenerator {
	private MessageDigest generator;
	private BigInteger MAX_HASHID;
	private static HashGenerator singleton = null;
	
	
	public static HashGenerator getInstance(){
		if(singleton!=null) {
			return singleton;
		}
		else {
			singleton = new HashGenerator();
			return singleton;
		}
		
	}
	
	public BigInteger GetMax_HASHID(){
		return MAX_HASHID;
	}
	
	public HashGenerator(){
		
		
		try {
			generator = MessageDigest.getInstance(Globals.hashType);
		} 
		catch (NoSuchAlgorithmException e) {
			// TODO Auto-generated catch block
			System.out.println("You need to fix the hash definition!");
			e.printStackTrace();
		}
		MAX_HASHID = (new BigInteger("2",10)).pow(512);//put the 
		
	}
	
	public HashID Hashify(byte[] input){
		byte[] hashval = generator.digest(input);
		return new HashID (new BigInteger(hashval));
	}
	

}
