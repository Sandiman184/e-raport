from run import app

# Vercel Serverless Function entry point
# This exposes the 'app' object to Vercel
if __name__ == '__main__':
    app.run()
