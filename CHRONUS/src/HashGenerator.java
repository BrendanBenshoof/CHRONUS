import java.math.BigInteger;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;


public class HashGenerator {
	private MessageDigest generator;
	
	public HashGenerator()
	{
		
		
		try {
			generator = MessageDigest.getInstance("SHA-512");
		} 
		catch (NoSuchAlgorithmException e) {
			// TODO Auto-generated catch block
			System.out.println("You need to fix the hash definition!");
			e.printStackTrace();
		}
	}
	
	public HashID Hashify(byte[] input)
	{
		byte[] hashval = generator.digest(input);
		return new HashID (new BigInteger(hashval));
	}
	

}
