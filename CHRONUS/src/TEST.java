public class TEST {

	public static void main(String[] args)
	{
		String test = "hello world";
		HashGenerator G = new HashGenerator();
		HashID H = G.Hashify(test.getBytes());
		System.out.println(H);
		
	}
	
}
