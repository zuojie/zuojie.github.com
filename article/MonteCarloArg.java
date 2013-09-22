public class MonteCarloArg extends Configured implements Tool {
    static private final Path TMP_DIR = new Path(
            "/home/arvinpeng/" + MonteCarloArg.class.getSimpleName() + "_TMP_3_141592654");
    static private final Long RAND_MAX = (1L << 63) - 1;
    public static boolean inCircle(double x, double y) {
        return x * x + y * y <= 1.0;
    }
    public static class MapC extends MapReduceBase 
            implements Mapper {
            public void map(LongWritable offset, LongWritable size, OutputCollectorout,
                    Reporter rep) throws IOException {
                double x = 0.0;
                double y = 0.0;
                long num_in = 0;
                long num = size.get();
                Random rand = new Random();
                for (long i = 0; i < num; ++ i) {
                    x = Math.abs((double)(rand.nextLong() * 1.0 / RAND_MAX));
                    y = Math.abs((double)(rand.nextLong() * 1.0 / RAND_MAX));
                    if (inCircle(x, y)) {
                        ++ num_in;
                    }
                    if (i % 1000 == 0) {
                        rep.setStatus("Generated " + i + " samples");
                    }
                }
                out.collect(new BooleanWritable(true), new LongWritable(num_in));
            }
    }

    public static class ReduceC extends MapReduceBase
            implements Reducer, NullWritable> {

        private long in_sum = 0;
        private JobConf conf; // configuration for accessing the file system

        @Override
        public void configure(JobConf job_conf) {
            conf = job_conf;
        }

        public void reduce(BooleanWritable key, Iterator val, 
                OutputCollector, NullWritable>out, Reporter rep) throws IOException {
            while(val.hasNext()) {
                in_sum += val.next().get();
            }
        }

        @Override
        public void close() throws IOException{
            Path out_path = new Path(TMP_DIR, "outputPi");
            Path out_file = new Path(out_path, "outPi.dat");
            FileSystem file_sys = FileSystem.get(conf);
            SequenceFile.Writer writer = SequenceFile.createWriter(file_sys, conf, out_file, 
                    LongWritable.class, NullWritable.class, CompressionType.NONE);
            writer.append(new LongWritable(in_sum), NullWritable.get());
            writer.close();
        }
    }

    public static void generateInputFile(FileSystem fsys, JobConf conf, Path in_dir, int num_sample, 
            long num_point) throws IOException {
        if (fsys.exists(TMP_DIR)) {
            throw new IOException(fsys.makeQualified(TMP_DIR) + " already exits!");
        } else if (!fsys.mkdirs(in_dir)) {
            throw new IOException("Can't create input directory " + in_dir);
        }
        for(int i = 0; i < num_sample; ++ i) {
            final Path in = new Path(in_dir, "part" + i);
            final LongWritable offset = new LongWritable(i * num_point); 
            final LongWritable size = new LongWritable(num_point);
            final SequenceFile.Writer writer = SequenceFile.createWriter(fsys, conf, 
                in, LongWritable.class, LongWritable.class, CompressionType.NONE);
            try {
                writer.append(offset, size);
            } finally {
                writer.close();
            }
            System.out.println("Wrote input for map # " + i);
        }
    }
    
    public static BigDecimal estimate(int ms, int rs, long size, JobConf jobConf) throws IOException {
        // set 
        jobConf.setJobName(MonteCarloArg.class.getSimpleName());
        jobConf.setInputFormat(SequenceFileInputFormat.class);
        jobConf.setOutputFormat(SequenceFileOutputFormat.class);
        jobConf.setMapOutputKeyClass(BooleanWritable.class);
        jobConf.setMapOutputValueClass(LongWritable.class);
        jobConf.setMapperClass(MapC.class);
        jobConf.setReducerClass(ReduceC.class);
        jobConf.setNumMapTasks(ms);
        jobConf.setNumReduceTasks(rs);
        // turn off speculative exec, because dfs doesn't handle multiple 
        // writers to the same file
        jobConf.setSpeculativeExecution(false);

        final Path in = new Path(TMP_DIR, "inputPi");
        final Path out = new Path(TMP_DIR, "outputPi");
        FileInputFormat.setInputPaths(jobConf, in);
        FileOutputFormat.setOutputPath(jobConf, out);
        FileSystem fsys = FileSystem.get(jobConf);
        try {
            generateInputFile(fsys, jobConf, in, ms, size); 
            System.out.println("Starting Hadoop Job");
            final long start_time = System.currentTimeMillis();
            JobClient.runJob(jobConf);
            final double duration = (System.currentTimeMillis() - start_time) / 1000.0;
            System.out.println("Job finished in " + duration + " seconds");

            // read file
            Path resFile = new Path(out, "outPi.dat");
            LongWritable in_circle = new LongWritable();
            SequenceFile.Reader reader = new SequenceFile.Reader(fsys, resFile, jobConf);
            try {
                reader.next(in_circle);
            } finally {
                reader.close();
            }
            return BigDecimal.valueOf(4).setScale(20).multiply(BigDecimal.valueOf(in_circle.get())).divide(
                    BigDecimal.valueOf(ms)).divide(BigDecimal.valueOf(size));
        } finally {
            //fsys.delete(TMP_DIR, true);
        }
    }

    public int run(String[] args) throws Exception {
        if (args.length != 3) {
           System.err.print("Usage " + getClass().getName() + "    "); 
           ToolRunner.printGenericCommandUsage(System.err);
           return -1;
        }
        final int MS = Integer.parseInt(args[0]);
        final int RS = Integer.parseInt(args[1]);
        final long NSAMPLES = Long.parseLong(args[2]); 
        System.out.println("number of maps " + MS);
        System.out.println("number of reduces " + RS);
        System.out.println("samples per map " + NSAMPLES);
        final JobConf JOBCONF = new JobConf(getConf(), getClass());
        final BigDecimal PI = estimate(MS, RS, NSAMPLES, JOBCONF); 
        System.out.println("Pi is = " + PI);
        return 0;
    }

    public static void main(String[] argv) throws Exception {
        int ret = ToolRunner.run(null, new MonteCarloArg(), argv);
        System.exit(ret);
    }
}
