import com.sun.org.apache.xml.internal.security.utils.Base64;

public class TEST {

	public static void main(String[] args)
	{
		String test = "hello world";
		String test2 = "Goodbye World";
		HashGenerator G = HashGenerator.getInstance();
		HashID H0 = G.Hashify(test.getBytes());
		HashID H1 = G.Hashify(test2.getBytes());
		System.out.println(H0);
		System.out.println(H1);
		System.out.println(Base64.encode(H0.getDistance(H1)));
		
	}
	
}
